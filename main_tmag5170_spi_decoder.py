# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
import tmag5170 as lbr

# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):

    DATA_TYPE_0h = "DATA_TYPE = 0h, Default 32-bit register access"
    DATA_TYPE_1h = "DATA_TYPE = 1h = 12-Bit XY data access"
    DATA_TYPE_2h = "DATA_TYPE = 2h = 12-Bit XZ data access"
    DATA_TYPE_3h = "DATA_TYPE = 3h = 12-Bit ZY data access"
    DATA_TYPE_4h = "DATA_TYPE = 4h = 12-Bit XT data access"
    DATA_TYPE_5h = "DATA_TYPE = 5h = 12-Bit YT data access"
    DATA_TYPE_6h = "DATA_TYPE = 6h = 12-Bit ZT data access"
    DATA_TYPE_7h = "DATA_TYPE = 7h = 12-Bit AM data access"

    str_data_type_mapping = { 
        DATA_TYPE_0h : lbr.tmga5170_frame_decoder.DataType.default_32bit_access,
        DATA_TYPE_1h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_XY,
        DATA_TYPE_2h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_XZ,
        DATA_TYPE_3h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_ZY,
        DATA_TYPE_4h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_temperature_XT,
        DATA_TYPE_5h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_temperature_YT,
        DATA_TYPE_6h : lbr.tmga5170_frame_decoder.DataType.magnetic_field_temperature_ZT,
        DATA_TYPE_7h : lbr.tmga5170_frame_decoder.DataType.angle_magnitude
        }

    DATA_TYPE_MAGNETIC_FIELD_ONLY_STRING = "DATA_TYPE = 1h-3h, 12-Bit XY/XZ/ZY data access"
    DATA_TYPE_MAGNETIC_FIELD_AND_TEMPERATURE_STRING = "DATA_TYPE = 4h-6h, 12-Bit XT/YT/ZT data access"
    DATA_TYPE_ANGLE_AND_MAGNITUDE_STRING = "DATA_TYPE = 7h, 12-Bit AM data access"
    DATA_TYPE = ChoicesSetting(choices=(DATA_TYPE_0h, DATA_TYPE_1h, DATA_TYPE_2h, DATA_TYPE_3h, DATA_TYPE_4h, DATA_TYPE_5h, DATA_TYPE_6h, DATA_TYPE_7h))

    FRAME_LENGTH_VERIF_ENABLED = "Discard data when length of data is not equal to 4 bytes"
    FRAME_LENGTH_VERIF_DISABLED = "Try to decode next frames when length is at least 4 bytes"
    Frame_length_verification = ChoicesSetting(choices=(FRAME_LENGTH_VERIF_ENABLED,FRAME_LENGTH_VERIF_DISABLED))

    TEMPERATURE_ANGLE_CONVERSION_ENABLED = "Temperature and Angle conversion to SI unit ENABLED"
    TEMPERATURE_ANGLE_CONVERSION_DISABLED = "Temperature and Angle conversion to SI unit DISABLED"

    str_temp_angle_conv_mapping = { 
        TEMPERATURE_ANGLE_CONVERSION_ENABLED:  lbr.tmga5170_frame_decoder.Temp_Angle_Conv.enabled ,
        TEMPERATURE_ANGLE_CONVERSION_DISABLED: lbr.tmga5170_frame_decoder.Temp_Angle_Conv.disabled ,
        }


    Temperature_Angle_Conversion = ChoicesSetting(choices=(TEMPERATURE_ANGLE_CONVERSION_ENABLED,TEMPERATURE_ANGLE_CONVERSION_DISABLED))

    A1_50MT = "±50mT (TMAG5170A1)"
    A1_25MT = "±25mT (TMAG5170A1)"
    A1_100MT = "±100mT (TMAG5170A1)"

    A2_150MT = "±150mT (TMAG5170A2)"
    A2_75MT = "±75mT (TMAG5170A2)"
    A2_300MT = "±300mT (TMAG5170A2)"

    RANGE_NOT_SELECTED = "-"

    str_range_mapping = { 
        A1_50MT:            lbr.tmga5170_frame_decoder.Br_range.TMAG5170A1_50mT_0h ,
        A1_25MT:            lbr.tmga5170_frame_decoder.Br_range.TMAG5170A1_25mT_1h ,
        A1_100MT:           lbr.tmga5170_frame_decoder.Br_range.TMAG5170A1_100mT_2h,
        A2_150MT:           lbr.tmga5170_frame_decoder.Br_range.TMAG5170A2_150mT_0h,
        A2_75MT:            lbr.tmga5170_frame_decoder.Br_range.TMAG5170A2_75mT_1h ,
        A2_300MT:           lbr.tmga5170_frame_decoder.Br_range.TMAG5170A2_300mT_2h,
        RANGE_NOT_SELECTED: lbr.tmga5170_frame_decoder.Br_range.TMAG5170_NotSelected
        }


    X_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))
    Y_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))
    Z_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'tmag5170_regular': {
            'format': \
            '{{data.length_err_msg}} \
            {{data.register_name}}-{{data.register_address}}, \
            R/W:{{data.read_write}}, \
            mosi:{{data.crc_mosi_correct}}, \
            miso:{{data.crc_miso_correct}}, \
            decoded_reg_val:{{data.register_decoding}}, \
            FrameCnt_debug:{{data.FrameCnt_debug}},\
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            crc_mosi_from_bus: {{data.mosi_crc_from_bus}},\
            crc_miso_expected: {{data.miso_crc_calculated}}, \
            crc_miso_from_bus: {{data.miso_crc_from_bus}}, \
            reg_val:{{data.register_value}}' \
        },
        'tmag5170_special': {
            'format': \
            '{{data.length_err_msg}} \
            {{data.register_name}}-{{data.register_address}}, \
            ch1_value:{{data.ch1_value}} {{data.ch1_si_value_str}}, \
            ch2_value:{{data.ch2_value}} {{data.ch2_si_value_str}}, \
            mosi:{{data.crc_mosi_correct}}, \
            miso:{{data.crc_miso_correct}}, \
            R/W:{{data.read_write}}, \
            decoded_reg_val:{{data.register_decoding}}, \
            FrameCnt_debug:{{data.FrameCnt_debug}},\
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            crc_mosi_from_bus: {{data.mosi_crc_from_bus}},\
            crc_miso_expected: {{data.miso_crc_calculated}}, \
            crc_miso_from_bus: {{data.miso_crc_from_bus}},\
            reg_val:{{data.register_value}}' \
        }
    }
    
    

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        self.decoder = lbr.tmga5170_frame_decoder(data_type = self.str_data_type_mapping[self.DATA_TYPE], 
                                              Br_X_axis_enum = self.str_range_mapping[self.X_RANGE], 
                                              Br_Y_axis_enum = self.str_range_mapping[self.Y_RANGE], 
                                              Br_Z_axis_enum = self.str_range_mapping[self.Z_RANGE],
                                              TempAngleConvEn = self.str_temp_angle_conv_mapping[self.Temperature_Angle_Conversion])

        self.frame_data_MISO = bytearray(b'')
        self.frame_data_MOSI = bytearray(b'')
        self.start_frame_label_time = None
        self.end_frame_label_time = None
        self.counter = 0

    def generateAnalyzerFrame(self):

            length_err_msg = self.decoder.set_mosi_miso_raw_data(self.frame_data_MOSI, self.frame_data_MISO)
            mosi_frame, miso_frame = self.decoder.get_mosi_miso_str()
            miso_crc_group, mosi_crc_group, cmd_stat_4_bit_group = self.decoder.get_4_bit_crc_cmd_stat_group()

            if self.DATA_TYPE == self.DATA_TYPE_0h:
                address_8bit_register_16bit_group, stat_8_bit_group = self.decoder.get_register_16_bit_address_stat_8_bit_group()
                read_write = address_8bit_register_16bit_group.read_write
                register_name = address_8bit_register_16bit_group.register_name

                AnalyzerFrameType = 'tmag5170_regular'
                AnalyzerFrameDictionary = {\
                        'length_err_msg':length_err_msg,                                                                        \
                        'mosi_frame':mosi_frame,                                                                                \
                        'mosi_crc_calculated':lbr.int_to_hex_string(mosi_crc_group.crc_calculated),                             \
                        'mosi_crc_from_bus':lbr.int_to_hex_string(mosi_crc_group.crc_from_bus),                                 \
                        'crc_mosi_correct':mosi_crc_group.crc_status,                                                           \
                        'miso_frame':miso_frame,                                                                                \
                        'miso_crc_calculated':lbr.int_to_hex_string(miso_crc_group.crc_calculated),                             \
                        'miso_crc_from_bus':lbr.int_to_hex_string(miso_crc_group.crc_from_bus),                                 \
                        'crc_miso_correct':miso_crc_group.crc_status,                                                           \
                        'read_write':read_write,                                                                                \
                        'register_address':lbr.int_to_hex_string(address_8bit_register_16bit_group.register_address),           \
                        'register_name':register_name,                                                                          \
                        'register_value':lbr.int_to_hex_string(address_8bit_register_16bit_group.register_value, 4),            \
                        'register_decoding':address_8bit_register_16bit_group.register_decoding,                                \
                        'stat_2_0':lbr.int_to_hex_string(cmd_stat_4_bit_group.stat_2_0),                                        \
                        'error_stat':lbr.int_to_hex_string(cmd_stat_4_bit_group.error_stat),                                    \
                        't_stat':lbr.int_to_hex_string(stat_8_bit_group.t_stat),                                                \
                        'z_stat':lbr.int_to_hex_string(stat_8_bit_group.z_stat),                                                \
                        'y_stat':lbr.int_to_hex_string(stat_8_bit_group.y_stat),                                                \
                        'x_stat':lbr.int_to_hex_string(stat_8_bit_group.x_stat),                                                \
                        'afe_alrt_status0_stat':lbr.int_to_hex_string(stat_8_bit_group.afe_alrt_status0_stat),                  \
                        'sys_alrt_status1_stat':lbr.int_to_hex_string(stat_8_bit_group.sys_alrt_status1_stat),                  \
                        'cfg_reset_stat':lbr.int_to_hex_string(stat_8_bit_group.cfg_reset_stat),                                \
                        'prev_crc_stat':lbr.int_to_hex_string(stat_8_bit_group.prev_crc_stat),                                  \
                        'cmd3':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd3),                                                \
                        'cmd2':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd2),                                                \
                        'cmd1':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd1),                                                \
                        'cmd0':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd0),                                                \
                        'FrameCnt_debug':self.counter,                                                                          \
                }
                
            else:
                data_24_bit_group = self.decoder.get_24_bit_data_group()
                read_write = data_24_bit_group.read_write
                register_name = data_24_bit_group.register_name

                AnalyzerFrameType = 'tmag5170_special'
                AnalyzerFrameDictionary = {\
                        'length_err_msg':length_err_msg,                                                                        \
                        'mosi_frame':mosi_frame,                                                                                \
                        'mosi_crc_calculated':lbr.int_to_hex_string(mosi_crc_group.crc_calculated),                             \
                        'mosi_crc_from_bus':lbr.int_to_hex_string(mosi_crc_group.crc_from_bus),                                 \
                        'crc_mosi_correct':mosi_crc_group.crc_status,                                                           \
                        'miso_frame':miso_frame,                                                                                \
                        'miso_crc_calculated':lbr.int_to_hex_string(miso_crc_group.crc_calculated),                             \
                        'miso_crc_from_bus':lbr.int_to_hex_string(miso_crc_group.crc_from_bus),                                 \
                        'crc_miso_correct':miso_crc_group.crc_status,                                                           \
                        'read_write':read_write,                                                                                \
                        'register_address':lbr.int_to_hex_string(data_24_bit_group.register_address),                           \
                        'register_name':register_name,                                                                          \
                        'register_value':lbr.int_to_hex_string(data_24_bit_group.register_value, 4),                            \
                        'register_decoding':data_24_bit_group.register_decoding,                                                \
                        'ch1_value':data_24_bit_group.ch1_value,                                                                \
                        'ch1_si_value_str':data_24_bit_group.ch1_si_value_str,                                                  \
                        'ch2_value':data_24_bit_group.ch2_value,                                                                \
                        'ch2_si_value_str':data_24_bit_group.ch2_si_value_str,                                                  \
                        'stat_2_0':lbr.int_to_hex_string(cmd_stat_4_bit_group.stat_2_0),                                        \
                        'error_stat':lbr.int_to_hex_string(cmd_stat_4_bit_group.error_stat),                                    \
                        'cmd3':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd3),                                                \
                        'cmd2':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd2),                                                \
                        'cmd1':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd1),                                                \
                        'cmd0':lbr.int_to_hex_string(cmd_stat_4_bit_group.cmd0),                                                \
                        'FrameCnt_debug':self.counter,                                                                          \
                }
            retVal = AnalyzerFrame(AnalyzerFrameType, self.start_frame_label_time, self.end_frame_label_time, AnalyzerFrameDictionary)
            print(f"FrameCnt_debug: {self.counter: >6}, mosi_f: {mosi_frame: >10}, crc_mosi: {mosi_crc_group.crc_status: >{len(lbr.CRC_ERROR_TOKEN)}}, miso_f: {miso_frame: >10}, crc_miso: {miso_crc_group.crc_status: >{len(lbr.CRC_ERROR_TOKEN)}}, read_write: {read_write: >6}, reg name:{register_name}")
            self.counter = self.counter + 1
            self.end_frame_label_time = None
            self.start_frame_label_time = None
            self.frame_data_MISO = bytearray(b'')
            self.frame_data_MOSI = bytearray(b'')
            return retVal

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        retVal = None
        
        if(frame.type == "enable"):
            self.start_frame_label_time = frame.start_time

        if(frame.type == "disable"):
            self.end_frame_label_time = frame.start_time
            retVal = self.generateAnalyzerFrame()


        if(frame.type == "result"):
            if self.Frame_length_verification == self.FRAME_LENGTH_VERIF_DISABLED:
                if (len(self.frame_data_MISO) == lbr.TMAG5170_SINGLE_FRAME_BYTE_SIZE) or (len(self.frame_data_MOSI) == lbr.TMAG5170_SINGLE_FRAME_BYTE_SIZE):
                    self.end_frame_label_time = frame.start_time
                    retVal = self.generateAnalyzerFrame()
                    self.start_frame_label_time = frame.start_time

            self.frame_data_MISO += frame.data['miso']
            self.frame_data_MOSI += frame.data['mosi']

        # Return the data frame itself
        return retVal

