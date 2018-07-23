#!/usr/bin/python3
#-*- coding: UTF-8 -*-

"""
Usage:
    * Run this script get file serialization_question_data which store the
      questions data.
    * cp this file to django project file which contain manager.py.
    * Run `python manager.py shell` to start interactive console.
    * Run code below:
    ```
    import pickle
    from potato.models import Question

    with open('./serialization_question_data', 'rb') as file:
        questions = pickle.load(file)

    for question in questions:
        q = Question(**question)
        q.save()
    ```
"""

from pymongo import MongoClient, ASCENDING
from html2text import html2text
import pickle


def work():
    """
    Get data from old db(mongodb) and clean HTML tags to markdown.
    After that save question datas into new postgres database.
    """
    # Get data from mongodb
    m_client = MongoClient('localhost', 27017)
    m_cursor = m_client.npoj_db.problems.find({}, sort=[('problemID', ASCENDING)])

    raw_datas = [data for data in m_cursor]
    new_datas = []

    # Clean HTML tags
    for data in raw_datas:
        if data['problemID'] == 0:
            continue
        print("id: {} | {}".format(
            data['problemID'],
            data['title']))
        _data = {}
        _data['description'] = html2text(data['description'])
        _data['title'] = data['title']
        try:
            _data['source'] = html2text(data['source'])
        except KeyError:
            _data['source'] = ""
        _data['description_input'] = html2text(data['input'])
        _data['description_output'] = html2text(data['output'])
        _data['sample_input'] = data['sampleInput']
        _data['sample_output'] = data['sampleOutput']
        _data['time_limit'] = int(data['timeLimit'])
        _data['memory_limit'] = int(data['memoryLimit']) * 1024
        _data['is_special_judge'] = data['spj']
        _data['hint'] = html2text(data['hint'])
        new_datas.append(_data)

    with open('./serialization_question_data', 'wb') as file:
        pickle.dump(new_datas, file)


if __name__ == '__main__':
    work()
