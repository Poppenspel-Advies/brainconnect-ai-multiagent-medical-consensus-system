from google.protobuf import any_pb2 as _any_pb2
from ...google.rpc import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(_message.Message):
    __slots__ = ("name", "metadata", "done", "error", "response")
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    name: str
    metadata: _any_pb2.Any
    done: bool
    error: _status_pb2.Status
    response: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., metadata: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., done: bool = ..., error: _Optional[_Union[_status_pb2.Status, _Mapping]] = ..., response: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class GetOperationRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...
