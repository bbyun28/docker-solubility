# -*- coding: utf-8 -*-
'''
Runs prediction model for graph convolution
Rodrigo Zepeda rzepeda17@gmail.com

'''
import time
import pandas as pd
import sys
import warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

#Importing deepchem throws a numpy warning
sys.stderr = None            # suppress deprecation warning
import deepchem as dc
sys.stderr = sys.__stderr__  # restore stderr

from deepchem.models import DAGModel
from deepchem.utils.save import load_from_disk
from rdkit import Chem

#Tell user which model we are running
print('Predicting with DAG Model...')

#Featurize molecules
featurizer = dc.feat.ConvMolFeaturizer()

#Read molecule model from folder
try:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore",category=UserWarning)
        model = DAGModel.load_from_dir("/usr/src/models/dag_model")
except:
    sys.exit('Unable to find dag model at "/usr/src/models/dag_model"')

#Read dataset to predict
try:
    newsmiles = pd.read_csv('/data/To_predict.csv') #TODO: Allow to read any file on data
except:
    sys.exit('Unable to read "To_predict.csv" from "/data" directory')

try:
    mols = [Chem.MolFromSmiles(s) for s in newsmiles.loc[:,"Smiles"]]
except:
    sys.exit('Unable to read "Smiles" column from "To_predict.csv"')

#Featurize data
x = featurizer.featurize(mols)
transformer = dc.trans.DAGTransformer(max_atoms=max_atoms)

#Predict molecules
predicted_solubility = model.predict_on_batch(x)

#Convert to dataframe
mydf = pd.concat([newsmiles, pd.DataFrame(predicted_solubility)], axis = 1)
mydf.columns = ["Smile","Predicted Solubility"]

#Get file name
fname = 'PredictedDAG ' + time.ctime() + '.csv'

#Write dataset
try:
    mydf.to_csv('/data/' + fname, index=False)
    print('Model saved as "' + fname + '" on "/data" directory')
except:
    sys.exit('Unable to write "' + fname + '" on "/data" directory')