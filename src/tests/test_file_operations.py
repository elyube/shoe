import pytest
import pathlib
import json
import os
from .. import file_operations as fo

class Test_FileOperations:

    __CURRENT_DIR = pathlib.Path(__file__).parent

    __TESTER_JSON = __CURRENT_DIR / "tester.json"
    __FAILS_JSON = __CURRENT_DIR / "fail.json"

    def test_GetsListFromJson(self):
        a = fo.ReadFromJsonFile(Test_FileOperations.__TESTER_JSON)

        assert type(a) is list
        assert len(a) > 0

        for obj in a:
            assert type(obj) is dict

    
    def test_EmptyIfNotJsonList(self):
        a = fo.ReadFromJsonFile(Test_FileOperations.__FAILS_JSON)

        assert type(a) is list
        assert len(a) == 0

    
    def test_AppendsJsonList(self):
        jason = [
            {
                "index" : 0
            },
            {
                "index" : 1
            }
        ]

        path = Test_FileOperations.__CURRENT_DIR / "temp.json"
        temp_file = open(file=path, mode="wt")
        json.dump(jason, temp_file)
        temp_file.close()

        read = fo.ReadFromJsonFile(path=path)
        assert len(read) == 2

        appendix = [
            {
                "index" : 2
            }
        ]
        added = fo.AppendJsonFile(path=path, new_list=appendix)
        assert added is True
        result = fo.ReadFromJsonFile(path=path)
        assert len(result) == 3
        i = 0
        for obj in result:
            assert obj["index"] == i
            i = i + 1
        os.remove(path=path)