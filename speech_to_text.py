# -*- coding: utf-8 -*-
import argparse

import stt_service_pb2
import stt_service_pb2_grpc

import os
import requests
import json
import grpc

import subprocess

CHUNK_SIZE = 16000

PREFIX = 'exten-401-'
ROOT_DIR = 'Asterisk'
FOLDER_ID = 'b1gp' # TODO
PASSPORT_TOKEN = 'AQAE' # TODO


def gen(folder_id, audio_file_name):
    # Задаем настройки распознавания.
    specification = stt_service_pb2.RecognitionSpec(
        language_code='ru-RU',
        profanity_filter=True,
        model='general',
        partial_results=True,
        audio_encoding='OGG_OPUS',
        sample_rate_hertz=8000
    )
    streaming_config = stt_service_pb2.RecognitionConfig(specification=specification, folder_id=folder_id)
    # Отправляем сообщение с настройками распознавания.
    yield stt_service_pb2.StreamingRecognitionRequest(config=streaming_config)

    # Читаем аудиофайл и отправляем его содержимое порциями.
    with open(audio_file_name, 'rb') as f:
        data = f.read(CHUNK_SIZE)
        while data != b'':
            yield stt_service_pb2.StreamingRecognitionRequest(audio_content=data)
            data = f.read(CHUNK_SIZE)


def run(folder_id, iam_token, audio_file_name):

    data = ''
    status_name = ''
    # Устанавливаем соединение с сервером.
    cred = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
    stub = stt_service_pb2_grpc.SttServiceStub(channel)

    # Отправляем данные для распознавания.
    print 'START: ', audio_file_name
    it = stub.StreamingRecognize(gen(folder_id, audio_file_name + '.ogg'),
                                 metadata=(('authorization', 'Bearer %s' % iam_token),))

    # Обрабатываем ответы сервера и выводим результат в консоль.
    try:
        for r in it:
            try:
                if r.chunks[0].final:
                    data += r.chunks[0].alternatives[0].text + ' '
            except LookupError:
                print('Not available chunks')

    except grpc._channel._Rendezvous as err:
        print 'ERROR: ', audio_file_name
        print('Error code %s, message: %s' % (err._state.code, err._state.details))
    else:
        print 'COMPLETE: ', audio_file_name
    print data.encode('utf-8')
    with open(audio_file_name + '.txt', 'w+') as output:
        output.write(data.encode('utf-8'))


def get_token(passport_token):
    response = requests.post(
        url='https://iam.api.cloud.yandex.net/iam/v1/tokens',
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "yandexPassportOauthToken": passport_token,
        }),
    )
    print 'get_token: success'
    return json.loads(response.content)['iamToken']


def get_paths(top_dir):
    path_buf = []
    for root, dirs, files in os.walk(top_dir):
        for name in files:
            path_name = os.path.join(root, name)
            if PREFIX in name \
                    and name.endswith('.wav') \
                    and os.stat(path_name).st_size > 4000:
                path_buf.append(path_name)

    if len(path_buf):
        print 'paths for get_ogg:\n', path_buf
    else:
        print 'path_buf is empty\n'
    return path_buf


def get_ogg(path):
    subprocess.check_call(
        [
            'ffmpeg',
            '-i',
            path,
            '-acodec',
            'libvorbis',
            path + '.ogg',
        ],
        shell=True)
    print path + '.ogg was created'


if __name__ == '__main__':
    path_buf = get_paths(ROOT_DIR)
    token = get_token(PASSPORT_TOKEN)

    for path_name in path_buf:
        if not os.path.exists(path_name + '.ogg'):
            get_ogg(path_name)

    print 'conversion to .ogg is completed'

    for path_name in path_buf:
        if not os.path.exists(path_name + '.txt'):
            run(FOLDER_ID, token, path_name)
        else:
            print path_name + '.txt already exists'
