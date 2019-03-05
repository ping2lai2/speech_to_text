# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import stt_service_pb2 as stt__service__pb2


class SttServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.StreamingRecognize = channel.stream_stream(
        '/yandex.cloud.ai.stt.v2.SttService/StreamingRecognize',
        request_serializer=stt__service__pb2.StreamingRecognitionRequest.SerializeToString,
        response_deserializer=stt__service__pb2.StreamingRecognitionResponse.FromString,
        )


class SttServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def StreamingRecognize(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SttServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'StreamingRecognize': grpc.stream_stream_rpc_method_handler(
          servicer.StreamingRecognize,
          request_deserializer=stt__service__pb2.StreamingRecognitionRequest.FromString,
          response_serializer=stt__service__pb2.StreamingRecognitionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'yandex.cloud.ai.stt.v2.SttService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
