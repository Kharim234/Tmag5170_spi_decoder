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
        self.assertAlmostEqual(result, -267.033333333333, delta = 0.0001)

        result = self.decoder.convert_raw_temp_to_celsius(17522,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 25, delta = 0.0001)

        result = self.decoder.convert_raw_temp_to_celsius(20522,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 75, delta = 0.0001)

        result = self.decoder.convert_raw_temp_to_celsius(13622,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, -40, delta = 0.0001)

        result = self.decoder.convert_raw_temp_to_celsius(65535,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 825.216666666667, delta = 0.0001)

    def test_convert_raw_magnetic_field_to_miliTeslas(self):
        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(32767,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170_NotSelected)
        self.assertEqual(result, None)

        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(0,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 0, delta = 0.0001)

        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(32767,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 149.995422363281, delta = 0.0001)

        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(-32768,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, -150, delta = 0.0001)

        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(16000,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 73.2421875, delta = 0.0001)

        result = self.decoder.convert_raw_magnetic_field_to_miliTeslas(-16000,tmga5170_frame_decoder.DataType.default_32bit_access,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, -73.2421875, delta = 0.0001)

    def test_convert_raw_angle_to_deg(self):
        result = self.decoder.convert_raw_angle_to_deg(0,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 0, delta = 0.0001)

        result = self.decoder.convert_raw_angle_to_deg(0x1628,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 354.50, delta = 0.0001)

        result = self.decoder.convert_raw_angle_to_deg(0x0114,tmga5170_frame_decoder.DataType.default_32bit_access)
        self.assertAlmostEqual(result, 17.25, delta = 0.0001)

    def test_convert_temparature_threshold_to_celsius(self):

        result = self.decoder.convert_temparature_threshold_to_celsius(103,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR_TEMP)
        self.assertAlmostEqual(result, 172, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(90,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR_TEMP)
        self.assertAlmostEqual(result, 116.529, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(80,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR_TEMP)
        self.assertAlmostEqual(result, 73.859, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(70,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR,tmga5170_frame_decoder.DEFAULT_VALUE_HI_THR_TEMP)
        self.assertAlmostEqual(result, 31.189, delta = 0.0001)

        result = self.decoder.convert_temparature_threshold_to_celsius(50,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR_TEMP)
        self.assertAlmostEqual(result, -53, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(40,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR_TEMP)
        self.assertAlmostEqual(result, -95.67, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(60,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR_TEMP)
        self.assertAlmostEqual(result, -10.33, delta = 0.0001)
        result = self.decoder.convert_temparature_threshold_to_celsius(70,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR,tmga5170_frame_decoder.DEFAULT_VALUE_LO_THR_TEMP)
        self.assertAlmostEqual(result, 32.34, delta = 0.0001)



    def test_convert_magnetic_field_threshold_to_miliTeslas(self):
        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(0,tmga5170_frame_decoder.Br_range.TMAG5170_NotSelected)
        self.assertEqual(result, None)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(0,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 0, delta = 0.0001)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(127,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 148.828125, delta = 0.0001)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(-128,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, -150, delta = 0.0001)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(60,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 70.3125, delta = 0.0001)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(-50,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, -58.59375, delta = 0.0001)

        result = self.decoder.convert_magnetic_field_threshold_to_miliTeslas(125,tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h)
        self.assertAlmostEqual(result, 146.484375, delta = 0.0001)

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