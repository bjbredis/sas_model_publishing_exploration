from flask import Flask, jsonify
import pandas as pd
import os
import swat
# import json

app = Flask(__name__)


# app vars: 
cas_session = []
modeltbl = {}
description_json = {}  # json document description of the model parameters
cas_library = "public" # name of the CAS library in which this astore model is stored
model_name = "gb_model_astore"  # filename of astore model
model_filename = "gb_model_astore.bin.sashdat"  # filename of astore model
model_description = [] # 

##
# GET on '/inputs', '/outputs', and '/description' will describe the API 
# endpoints and model inputs / outputs
##
@app.route('/inputs', methods=['GET'])
def describe_model_inputs():
    if 'InputVariables' in model_description:
        return model_description.InputVariables.to_json()
    else: 
        return {}

@app.route('/outputs', methods=['GET'])
def describe_model_outputs():
    if 'OutputVariables' in model_description:
        return model_description.OutputVariables.to_json()
    else: 
        return {}
    
@app.route('/description', methods=['GET'])
def describe_model():
    if 'Description' in model_description:     
        return model_description.Description.to_json()
    else: 
        return {}

##
# PUT on '/' will score a record
##
@app.route('/', methods=['POST'])
def score_root():
    return 'POST on "/" does nothing. Try /score instead.' + str(os.getenv("CF_INSTANCE_INDEX", 0))

##
# PUT on '/' will score a record
##
@app.route('/score', methods=['POST'])
def score_record():
    return 'POST on "/score".' + str(os.getenv("CF_INSTANCE_INDEX", 0))


## 
# main app entry point
##
if __name__ == "__main__":
    if os.environ.get('VCAP_SERVICES') is None: 
    	# running locally, let's debug
        PORT = 8989
        DEBUG = True
    else:          
    	# running in cloudfoundry                             
        PORT = int(os.getenv("PORT"))
        DEBUG = False

    # connect to CAS with which creds? caslib=cas_library
    #
    # auth using authinfo file in local filesystem will be a problem in CF
    cas_session = swat.CAS(hostname="bbviya3.pre-sal.sashq-r.openstack.sas.com", port=5570,
                           authinfo='/home/centos/.authinfo',
                           caslib=cas_library, name="brad")
    
    # load a few required CAS action sets
    results = cas_session.loadactionset('astore')
    results = cas_session.loadactionset('decisiontree')
    
    if DEBUG:
        print(cas_session)
    
    # create a reference to the model table;
    modeltbl = cas_session.CASTable(name=model_name, caslib=cas_library)
    
    if DEBUG:
        print(cas_session.table.fileinfo(caslib=cas_library,path="%"))
    
    # upload it from a server side file if it doesn't already exist
    if not modeltbl.tableexists().exists:
        modeltbl = cas_session.upload_file(model_filename,casout=modeltbl)
        
    # get the model description one time
    model_description = cas_session.describe(rstore=dict(name=model_name,caslib=cas_library)) 

    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
