#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Yoann QUERET <yoann@queret.net>
"""

"""
This file is part of ODR-EncoderManager.

ODR-EncoderManager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ODR-EncoderManager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ODR-EncoderManager.  If not, see <http://www.gnu.org/licenses/>.
"""

import ConfigParser
import os
import sys
import json
import stat

class Config():
	def __init__(self, config_file):
		self.config_file = config_file
		self.load(config_file)
			
	def load(self, config_file):
		with open(self.config_file) as data_file:    
			self.config = json.load(data_file)

	def write(self, config):
		try:
			with open(self.config_file, 'w') as outfile:
				data = json.dumps(config, indent=4, separators=(',', ': '))
				outfile.write(data)
		except Exception as e:
			raise ValueError( str(e) )

	def generateSupervisorFiles(self, config):
		supervisorConfig = ""
		# Write supervisor pad-encoder section
		if config['odr']['padenc']['enable'] == 'true':
			command = config['odr']['path']['padenc_path']
			if config['odr']['padenc']['slide_directory'].strip() != '':
				# Check if config.mot_slide_directory exist
				if os.path.exists(config['odr']['padenc']['slide_directory']):
					command += ' --dir=%s' % (config['odr']['padenc']['slide_directory'])
					if config['odr']['padenc']['slide_once'] == 'true':
						command += ' --erase'
						
			# Check if config.mot_dls_fifo_file exist and create it if needed.
			if not os.path.isfile(config['odr']['padenc']['dls_fifo_file']):
				try:
					f = open(config['odr']['padenc']['dls_fifo_file'], 'w')
					f.close()
				except Exception as e:
					raise ValueError( 'Error when create DLS fifo file', str(e) )
			else:
				if config['odr']['source']['type'] == 'stream':
					try:
						f = open(config['odr']['padenc']['dls_fifo_file'], 'w')
						f.write('')
						f.close()
					except Exception,e:
						raise ValueError( 'Error when writing into DLS fifo file', str(e) )
				
			# Check if config.mot_pad_fifo_file exist and create it if needed.
			if not os.path.exists(config['odr']['padenc']['pad_fifo_file']):
				try:
					os.mkfifo(config['odr']['padenc']['pad_fifo_file'])
				except Exception,e:
					raise ValueError( 'Error when create PAD fifo file', str(e) )
			else:
				if not stat.S_ISFIFO(os.stat(config['odr']['padenc']['pad_fifo_file']).st_mode):
					#File %s is not a fifo file
					pass
			
			command += ' --sleep=%s' % (config['odr']['padenc']['slide_sleeping'])
			command += ' --pad=%s' % (config['odr']['padenc']['pad'])
			command += ' --dls=%s' % (config['odr']['padenc']['dls_fifo_file'])
			command += ' --output=%s' % (config['odr']['padenc']['pad_fifo_file'])
			
			if config['odr']['padenc']['raw_dls'] == 'true':
				command += ' --raw-dls'
				
			supervisorPadEncConfig = ""
			supervisorPadEncConfig += "[program:ODR-padencoder]\n"
			supervisorPadEncConfig += "command=%s\n" % (command)
			supervisorPadEncConfig += "autostart=true\n"
			supervisorPadEncConfig += "autorestart=true\n"
			supervisorPadEncConfig += "priority=10\n"
			supervisorPadEncConfig += "stderr_logfile=/var/log/supervisor/ODR-padencoder.err.log\n"
			supervisorPadEncConfig += "stdout_logfile=/var/log/supervisor/ODR-padencoder.log\n"
			
		# Write supervisor audioencoder section
		# Encoder path
		command = config['odr']['path']['encoder_path']
		
		# Input stream
		if config['odr']['source']['type'] == 'alsa':
			command += ' -d %s' % (config['odr']['source']['device'])
		if config['odr']['source']['type'] == 'stream':
			command += ' --vlc-uri=%s' % (config['odr']['source']['url'])
		if config['odr']['source']['driftcomp'] == 'true':
			command += ' -D'
		command += ' -b %s' % (config['odr']['output']['bitrate'])
		command += ' -r %s' % (config['odr']['output']['samplerate'])
		command += ' -c %s' % (config['odr']['output']['channels'])
		
		# DAB specific option
		if config['odr']['output']['type'] == 'dab':
			command += ' --dab'
			command += ' --dabmode=%s' % (config['odr']['output']['dab_dabmode'])
			command += ' --dabpsy=%s' % (config['odr']['output']['dab_dabpsy'])
		
		
		# DAB+ specific option
		if config['odr']['output']['type'] == 'dabp':
			if config['odr']['output']['dabp_sbr'] == 'true':
				command += ' --sbr'
			if config['odr']['output']['dabp_ps'] == 'true':
				command += ' --ps'
			if config['odr']['output']['dabp_sbr'] == 'false' and config['odr']['output']['dabp_ps'] == 'false':
				command += ' --aaclc'
			if config['odr']['output']['dabp_afterburner'] == 'false':
				command += ' --no-afterburner'
		
		# PAD encoder
		if config['odr']['padenc']['enable'] == 'true':
			if os.path.exists(config['odr']['padenc']['pad_fifo_file']) and stat.S_ISFIFO(os.stat(config['odr']['padenc']['pad_fifo_file']).st_mode):
				command += ' --pad=%s' % (config['odr']['padenc']['pad'])
				command += ' --pad-fifo=%s' % (config['odr']['padenc']['pad_fifo_file'])
				command += ' --write-icy-text=%s' % (config['odr']['padenc']['dls_fifo_file'])
		
		# Output
		hosts = config['odr']['output']['zmq_host'].replace(' ','').split(',')
		for host in hosts:
			command += ' -o tcp://%s' % (host)
				
		supervisorConfig = ""
		supervisorConfig += "[program:ODR-audioencoder]\n"
		supervisorConfig += "command=%s\n" % (command)
		supervisorConfig += "autostart=true\n"
		supervisorConfig += "autorestart=true\n"
		supervisorConfig += "priority=10\n"
		supervisorConfig += "stderr_logfile=/var/log/supervisor/ODR-audioencoder.err.log\n"
		supervisorConfig += "stdout_logfile=/var/log/supervisor/ODR-audioencoder.log\n"
		
		try:
			with open(config['global']['supervisor_file'], 'w') as supfile:
				supfile.write(supervisorConfig)
				if config['odr']['padenc']['enable'] == 'true':
					supfile.write('\n')
					supfile.write(supervisorPadEncConfig)
		except Exception,e:
			raise ValueError( 'Error when writing supervisor file', str(e) )