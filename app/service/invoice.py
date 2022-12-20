import os
import datetime

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import Config
from app.models import Invoice
from app import app

def tax_format(tar):
    if not tar:
        return 'No data'
    res = ''
    counter = 0
    while counter < len(tar):
        if (tar[counter]).isdecimal():
            res += (tar[counter])
        counter += 1
    if len(res) != 8:
        return 'error'
    return res

def price_format(tar):
    res = ''
    counter = 0
    while counter < len(tar):
        if (tar[counter]).isdecimal():
            res += (tar[counter])
        counter += 1
    return res

def id_format(tar):
    tar_arr = tar.split('-')
    if len(tar_arr[0]) != 2 or len(tar_arr[1]) != 8 or not (tar_arr[1]).isdecimal():
        return 'error'
    else:
        return tar

def date_format(tar):
    tar = tar.replace('/', ' ')
    tar = tar.replace('-', ' ')
    tar = tar.replace(':', ' ')

    datetime_object = datetime.datetime.strptime(tar, '%Y %m %d %H %M %S')
    return datetime_object

def recognition(id):
    
    invoice = Invoice.query.filter_by(id=id).first()
    # return invoice
    if invoice:
        # path = os.path.join(app.config['APP_DIRECTRY'], 'app')

        endpoint = app.config['AZURE_ENDPOINT']
        key = app.config['AZURE_KEY']
        credential = AzureKeyCredential(key)
        document_analysis_client = DocumentAnalysisClient(endpoint, credential)
        model_id = "modelForApp_1"
        # with open(, "rb") as fd:
        #     raise
        #     document = fd.read()
        path1 = os.path.join(app.config['APP_DIRECTRY'], 'app') + invoice.path
        with open(path1, "rb") as fd:
            # raise
            document = fd.read()
        poller = document_analysis_client.begin_analyze_document(model_id=model_id, document=document)
        result = poller.result()
        res_hash = {}
        for analyzed_document in result.documents:
            for name, field in analyzed_document.fields.items():
                if name == 'buy' or name == 'sale':
                    res_hash[name] = tax_format(field.value)
                elif name == 'id':
                    res_hash[name] = id_format(field.value)
                elif name == 'date':
                    res_hash[name] = date_format(field.value)
                elif name == 'price':
                    res_hash[name] = price_format(field.value)
        return res_hash

        