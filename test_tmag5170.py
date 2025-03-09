import unittest

from tmag5170 import tmga5170_frame_decoder







class TestDecoder(unittest.TestCase):
    def setUp(self):
        self.decoder = tmga5170_frame_decoder()

    def test_get_temperature_str(self):
        result = self.decoder.get_temperature_str(27.1)
        self.assertEqual(result, "[27.10 Celsius]")
        result = self.decoder.get_temperature_str(-100)
        self.assertEqual(result, "[-100.00 Celsius]")
        result = self.decoder.get_temperature_str(None)
        self.assertEqual(result, "")

    def test___X_CH_RESULT_DecodingFunction(self):
        result = self.decoder._tmga5170_frame_decoder__X_CH_RESULT_DecodingFunction(100)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")

    def test_convert_raw_temp_to_celsius(self):
        result = self.decoder.convert_raw_temp_to_celsius(0,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")

    def test_convert_raw_magnetic_field_to_miliTeslas(self):
        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(0,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170_NotSelected)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")

    def test_convert_raw_angle_to_deg(self):
        result = self.decoder.convert_raw_angle_to_deg(0,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")

    def test_convert_temparature_threshold_to_celsius(self):
        result = self.decoder.convert_temparature_threshold_to_celsius(0,0,0)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")

    def test_convert_magnetic_field_threshold_to_miliTeslas(self):
        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(0,tmga5170_frame_decoder.Br_range.TMAG5170_NotSelected)
        self.assertEqual(result, "[15-0] X_CH_RESULT: 100 ")




    def test_get_temperature_str(self):
        result = self.decoder.get_temperature_str(27.1)
        self.assertEqual(result, "[27.10 Celsius]")
        result = self.decoder.get_temperature_str(-100)
        self.assertEqual(result, "[-100.00 Celsius]")
        result = self.decoder.get_temperature_str(None)
        self.assertEqual(result, "")


    def tearDown(self):
        pass
if __name__ == "__main__":
    unittest.main()