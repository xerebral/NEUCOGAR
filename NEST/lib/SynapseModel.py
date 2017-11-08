import api_globals


class SynapseModel:
	"""
	Synapse object

	"""
	__synapse_user_model = ""
	__synapse_nest_model = ""
	__synapse_parameters = dict()
	__volume_transmitter = None
	__logger = api_globals.log.getLogger('SynapseModel')

	@staticmethod
	def int2Float(params_dict):
		for parameter, value in params_dict.items():
			if type(value) is int:
				params_dict[parameter] = float(value)
		return params_dict


	def getUserModel(self):
		return self.__synapse_user_model


	def buildSynapseSpec(self):
		"""
		Write parameters from user style to the NEST readable

		:return:
		"""
		new_params_dict = dict(self.__synapse_parameters)
		for parameter, value in new_params_dict.items():
			if type(value) is list:
				new_params_dict[ parameter ] = {
					'distribution' : 'uniform',
				    'low' : float(value[0]),
				    'high': float(value[1])
				}
		new_params_dict['model'] = self.getUserModel()
		return new_params_dict


	def __init__(self, user_model, nest_model, params):
		self.__synapse_user_model = user_model
		self.__synapse_nest_model = nest_model
		self.__synapse_parameters = dict(self.int2Float(params))

		self.__synapse_parameters['weight'] = self.__synapse_parameters['Wmax']

		# Create a volume transmitter for neuromodulators
		if nest_model in ["stdp_dopamine_synapse",
						  "stdp_serotonin_synapse",
						  "stdp_noradrenaline_synapse"]:
			self.__volume_transmitter = api_globals.NEST.Create("volume_transmitter")
			self.__synapse_parameters['vt'] = self.__volume_transmitter[0]
			# Create model with defaults parameters and volume transmitter
			api_globals.NEST.CopyModel(nest_model, 				                # NEST model name
									   user_model,				                # User model name
									   {'vt': self.__volume_transmitter[0]})    # Build parameters to NEST readable
		else:
			# Copy model with default parameters
			api_globals.NEST.CopyModel(nest_model, user_model)
		# Log actions
		self.__logger.info("{0} synapse ({1}) {2}".format(self.__synapse_user_model,
														  self.__synapse_nest_model,
														  "[+vt]" if self.__volume_transmitter else ""))

	def getVolumeTransmitter(self):
		return self.__volume_transmitter