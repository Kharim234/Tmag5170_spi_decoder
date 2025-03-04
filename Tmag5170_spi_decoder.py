# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
import collections
from enum import Enum

CRC_OK_TOKEN = "CRC_OK"
CRC_ERROR_TOKEN = "CRC_ERROR"
LENGTH_ERROR_TOKEN = "Length error"
WRITE_REGISTER_TOKEN = "write"
READ_REGISTER_TOKEN = "read"

READ_WRITE_BIT_POSITION = 31
REGISTER_ADDR_POSITION = 24
TMAG5170_16_BIT_SPI_DATA_POSITION = 8

REGISTER_ADDR_MASK = 0x7F
TMAG5170_16_BIT_SPI_DATA_MASK = 0xFFFF


TMAG5170_SINGLE_FRAME_BYTE_SIZE = 4

def get_masked_value (value: int, position: int, mask: int) -> int:
    return ((value  >> position)& mask) 

def get_bit (value: int, i: int) -> int:
    return (value >> i) & 0x01

def set_bit (bit_val: int, position: int) -> int:
    return (bit_val << position)

def set_bit_in_value (bit_val: int, position: int, value: int) -> int:
    return (set_bit(bit_val, position) | value)

def uint16_to_int16 (in_value: int) -> int:
    value = in_value.to_bytes(2, 'big')
    int_val = int.from_bytes(value, 'big', signed = True)
    return (int_val)

def uint8_to_int8 (in_value: int) -> int:
    value = in_value.to_bytes(1, 'big')
    int_val = int.from_bytes(value, 'big', signed = True)
    return (int_val)

def uintX_to_intX_represented_on_Y_bytes (in_value: int, size_of_in_value: int, out_bytes_count: int,) -> int:
    int_val = None
    if out_bytes_count > 0 and size_of_in_value > 0:
        value = in_value
        sign_bit = get_bit(in_value, size_of_in_value - 1)
        for i in range((size_of_in_value),(out_bytes_count * 8)):
            value = set_bit_in_value(sign_bit, i, value)
        byte_value = value.to_bytes(out_bytes_count, 'big')
        int_val = int.from_bytes(byte_value, 'big', signed = True)
    return (int_val)

def int_to_hex_string(value:int, leadingZeros:int = 0):
    if value == None:
        return ""
    else:
        hex_string = f"{value:X}"
        return f"0x{hex_string:0>{leadingZeros}}"
    
def int_none_verificatio(value:int):
    if value == None:
        return ""
    else:
        return value
class tmga5170_frame_decoder:
    class DataType(Enum):
        default_32bit_access = 0
        magnetic_field = 1
        magnetic_field_temperature = 2
        angle_magnitude = 3
    class Br_range(Enum):
        TMAG5170A1_50mT_0h = 0
        TMAG5170A1_25mT_1h = 1
        TMAG5170A1_100mT_2h = 2

        TMAG5170A2_150mT_0h = 3
        TMAG5170A2_75mT_1h = 4
        TMAG5170A2_300mT_2h = 5

        TMAG5170_NotSelected = 6

    Br_range_mapping = { 
        Br_range.TMAG5170A1_50mT_0h : 50,
        Br_range.TMAG5170A1_25mT_1h : 25,
        Br_range.TMAG5170A1_100mT_2h : 100,

        Br_range.TMAG5170A2_150mT_0h : 150,
        Br_range.TMAG5170A2_75mT_1h : 75,
        Br_range.TMAG5170A2_300mT_2h : 300
        }
    
    __tmag5170_mapping_type = collections.namedtuple('__tmag5170_mapping_type', ['Acronym', 'DecodingFunction'])
    crc_4_bit_group_type = collections.namedtuple('crc_4_bit_group_type', ['crc_status','crc_calculated','crc_from_bus'])
    cmd_stat_4_bit_group_type = collections.namedtuple('cmd_stat_4_bit_group_type', ['cmd3', 'cmd2', 'cmd1', 'cmd0', 'error_stat', 'stat_2_0'])
    address_8bit_register_16bit_group_type = collections.namedtuple('address_8bit_register_16bit_group_type', ['read_write','register_address','register_name','register_decoding','register_value'])
    stat_8_bit_group_type = collections.namedtuple('stat_8_bit_group_type', ['prev_crc_stat','cfg_reset_stat','sys_alrt_status1_stat','afe_alrt_status0_stat','x_stat','y_stat','z_stat','t_stat'])
    data_24_bit_group_type = collections.namedtuple('data_24_bit_group_type', ['read_write', 'ch1_value', 'ch2_value','register_address','register_name','register_decoding','register_value'])

    def __init__(self, enable__cmd_stat_4_bit_group = True, enable__stat_8_bit_group = True, crc_enabled = True, 
                 data_type: DataType  = DataType.default_32bit_access, 
                 Br_X_axis_enum :Br_range = Br_range.TMAG5170_NotSelected,
                 Br_Y_axis_enum :Br_range = Br_range.TMAG5170_NotSelected,
                 Br_Z_axis_enum :Br_range = Br_range.TMAG5170_NotSelected):
        self.__Tmag5170_register_mapping = {
            0x00: self.__tmag5170_mapping_type("DEVICE_CONFIG"    ,    self.__DEVICE_CONFIG_DecodingFunction)     ,
            0x01: self.__tmag5170_mapping_type("SENSOR_CONFIG"    ,    self.__SENSOR_CONFIG_DecodingFunction)     ,
            0x02: self.__tmag5170_mapping_type("SYSTEM_CONFIG"    ,    self.__SYSTEM_CONFIG_DecodingFunction)     ,
            0x03: self.__tmag5170_mapping_type("ALERT_CONFIG"     ,    self.__ALERT_CONFIG_DecodingFunction)      ,
            0x04: self.__tmag5170_mapping_type("X_THRX_CONFIG"    ,    self.__X_THRX_CONFIG_DecodingFunction)     ,
            0x05: self.__tmag5170_mapping_type("Y_THRX_CONFIG"    ,    self.__Y_THRX_CONFIG_DecodingFunction)     ,
            0x06: self.__tmag5170_mapping_type("Z_THRX_CONFIG"    ,    self.__Z_THRX_CONFIG_DecodingFunction)     ,
            0x07: self.__tmag5170_mapping_type("T_THRX_CONFIG"    ,    self.__T_THRX_CONFIG_DecodingFunction)     ,
            0x08: self.__tmag5170_mapping_type("CONV_STATUS"      ,    self.__CONV_STATUS_DecodingFunction)       ,
            0x09: self.__tmag5170_mapping_type("X_CH_RESULT"      ,    self.__X_CH_RESULT_DecodingFunction)       ,
            0x0A: self.__tmag5170_mapping_type("Y_CH_RESULT"      ,    self.__Y_CH_RESULT_DecodingFunction)       ,
            0x0B: self.__tmag5170_mapping_type("Z_CH_RESULT"      ,    self.__Z_CH_RESULT_DecodingFunction)       ,
            0x0C: self.__tmag5170_mapping_type("TEMP_RESULT"      ,    self.__TEMP_RESULT_DecodingFunction)       ,
            0x0D: self.__tmag5170_mapping_type("AFE_STATUS"       ,    self.__AFE_STATUS_DecodingFunction)        ,
            0x0E: self.__tmag5170_mapping_type("SYS_STATUS"       ,    self.__SYS_STATUS_DecodingFunction)        ,
            0x0F: self.__tmag5170_mapping_type("TEST_CONFIG"      ,    self.__TEST_CONFIG_DecodingFunction)       ,
            0x10: self.__tmag5170_mapping_type("OSC_MONITOR"      ,    self.__OSC_MONITOR_DecodingFunction)       ,
            0x11: self.__tmag5170_mapping_type("MAG_GAIN_CONFIG"  ,    self.__MAG_GAIN_CONFIG_DecodingFunction)   ,
            0x12: self.__tmag5170_mapping_type("MAG_OFFSET_CONFIG",    self.__MAG_OFFSET_CONFIG_DecodingFunction) ,
            0x13: self.__tmag5170_mapping_type("ANGLE_RESULT"     ,    self.__ANGLE_RESULT_DecodingFunction)      ,
            0x14: self.__tmag5170_mapping_type("MAGNITUDE_RESULT" ,    self.__MAGNITUDE_RESULT_DecodingFunction)
        }
        self.mosi_value = None
        self.miso_value = None
        self.enable__cmd_stat_4_bit_group = enable__cmd_stat_4_bit_group
        self.enable__stat_8_bit_group = enable__stat_8_bit_group
        self.crc_enabled = crc_enabled
        self.data_type = data_type
        self.Br_X_axis_enum = Br_X_axis_enum
        self.Br_Y_axis_enum = Br_Y_axis_enum
        self.Br_Z_axis_enum = Br_Z_axis_enum
    @staticmethod 
    def __MAG_OFFSET_CONFIG_DecodingFunction(data: int):
        OFFSET_SELECTION_15_14 = get_masked_value(data, 14,    0x0003)
        OFFSET_VALUE1__13_7    = get_masked_value(data, 7,    0x007F)
        OFFSET_VALUE2__6_0     = get_masked_value(data, 0,    0x007F)
        return    \
f"[15-14] OFFSET_SELECTION: {int_to_hex_string(OFFSET_SELECTION_15_14)}, \
[13-7] OFFSET_VALUE1: {uintX_to_intX_represented_on_Y_bytes(OFFSET_VALUE1__13_7, 7, 1)}, \
[6-0] OFFSET_VALUE2: {uintX_to_intX_represented_on_Y_bytes(OFFSET_VALUE2__6_0, 7, 1)}"

    @staticmethod 
    def __MAG_GAIN_CONFIG_DecodingFunction(data: int):
        GAIN_SELECTION_15_14 = get_masked_value(data, 14,    0x0003)
        RESERVED_13_11       = get_masked_value(data, 11,    0x0007)
        GAIN_VALUE_10_0      = get_masked_value(data, 10,    0x07FF)
        return    \
f"[15-14] GAIN_SELECTION: {int_to_hex_string(GAIN_SELECTION_15_14)}, \
[13-11] RESERVED: {int_to_hex_string(RESERVED_13_11)}, \
[10-0] GAIN_VALUE: {int_to_hex_string(GAIN_VALUE_10_0)}"

    @staticmethod
    def __ALERT_CONFIG_DecodingFunction(data: int):
        RESERVED_15_14      = get_masked_value(data, 14,    0x0003)
        ALERT_LATCH_13      = get_masked_value(data, 13,    0x0001)
        ALERT_MODE_12       = get_masked_value(data, 12,    0x0001)
        STATUS_ALRT_11      = get_masked_value(data, 11,    0x0001)
        RESERVED_10_9       = get_masked_value(data, 9,     0x0003)
        RSLT_ALRT_8         = get_masked_value(data, 8,     0x0001)
        RESERVED_7_6        = get_masked_value(data, 6,     0x0003)
        THRX_COUNT_5_4      = get_masked_value(data, 4,     0x0003)
        T_THRX_ALRT_3       = get_masked_value(data, 3,     0x0001)
        Z_THRX_ALRT_2       = get_masked_value(data, 2,     0x0001)
        Y_THRX_ALRT_1       = get_masked_value(data, 1,     0x0001)
        X_THRX_ALRT_0       = get_masked_value(data, 0,     0x0001)
        return    \
f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
[13] ALERT_LATCH: {int_to_hex_string(ALERT_LATCH_13)}, \
[12] ALERT_MODE: {int_to_hex_string(ALERT_MODE_12)}, \
[11] STATUS_ALRT: {int_to_hex_string(STATUS_ALRT_11)}, \
[10-9] RESERVED: {int_to_hex_string(RESERVED_10_9)}, \
[8] RSLT_ALRT: {int_to_hex_string(RSLT_ALRT_8)}, \
[7-6] RESERVED: {int_to_hex_string(RESERVED_7_6)}, \
[5-4] THRX_COUNT: {int_to_hex_string(THRX_COUNT_5_4)}, \
[3] T_THRX_ALRT: {int_to_hex_string(T_THRX_ALRT_3)}, \
[2] Z_THRX_ALRT: {int_to_hex_string(Z_THRX_ALRT_2)}, \
[1] Y_THRX_ALRT: {int_to_hex_string(Y_THRX_ALRT_1)}, \
[0] X_THRX_ALRT: {int_to_hex_string(X_THRX_ALRT_0)}"

    @staticmethod
    def __SYSTEM_CONFIG_DecodingFunction(data: int):
        RESERVED_15_14      = get_masked_value(data, 14,    0x0003)
        DIAG_SEL_13_12      = get_masked_value(data, 12,    0x0003)
        RESERVED_11         = get_masked_value(data, 11,    0x0001)
        TRIGGER_MODE_10_9   = get_masked_value(data, 9,     0x0003)
        DATA_TYPE_8_6       = get_masked_value(data, 6,     0x0007)
        DIAG_EN_5           = get_masked_value(data, 5,     0x0001)
        RESERVED_4_3        = get_masked_value(data, 3,     0x0003)
        Z_HLT_EN_2          = get_masked_value(data, 2,     0x0001)
        Y_HLT_EN_1          = get_masked_value(data, 1,     0x0001)
        X_HLT_EN_0          = get_masked_value(data, 0,     0x0001)
        return    \
f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
[13-12] DIAG_SEL: {int_to_hex_string(DIAG_SEL_13_12)}, \
[11] RESERVED: {int_to_hex_string(RESERVED_11)}, \
[10-9] TRIGGER_MODE: {int_to_hex_string(TRIGGER_MODE_10_9)}, \
[8-6] DATA_TYPE: {int_to_hex_string(DATA_TYPE_8_6)}, \
[5] DIAG_EN: {int_to_hex_string(DIAG_EN_5)}, \
[4-3] RESERVED: {int_to_hex_string(RESERVED_4_3)}, \
[2] Z_HLT_EN: {int_to_hex_string(Z_HLT_EN_2)}, \
[1] Y_HLT_EN: {int_to_hex_string(Y_HLT_EN_1)}, \
[0] X_HLT_EN: {int_to_hex_string(X_HLT_EN_0)}"

    @staticmethod
    def __SENSOR_CONFIG_DecodingFunction(data: int):
        ANGLE_EN_15_14      = get_masked_value(data, 14,    0x0003)
        SLEEPTIME_13_10     = get_masked_value(data, 10,    0x000F)
        MAG_CH_EN_9_6       = get_masked_value(data, 6,     0x000F)
        Z_RANGE_5_4         = get_masked_value(data, 4,     0x0003)
        Y_RANGE_3_2         = get_masked_value(data, 2,     0x0003)
        X_RANGE_1_0         = get_masked_value(data, 0,     0x0003)
        return    \
f"[15-14] ANGLE_EN: {int_to_hex_string(ANGLE_EN_15_14)}, \
[13-10] SLEEPTIME: {int_to_hex_string(SLEEPTIME_13_10)}, \
[9-6] MAG_CH_EN: {int_to_hex_string(MAG_CH_EN_9_6)}, \
[5-4] Z_RANGE: {int_to_hex_string(Z_RANGE_5_4)}, \
[3-2] Y_RANGE: {int_to_hex_string(Y_RANGE_3_2)}, \
[1-0] X_RANGE: {int_to_hex_string(X_RANGE_1_0)}"

    @staticmethod
    def __DEVICE_CONFIG_DecodingFunction(data: int):
        RESERVED_15         = get_masked_value(data, 15,    0x0001)
        CONV_AVG_14_12      = get_masked_value(data, 12,    0x0003)
        RESERVED_11_10      = get_masked_value(data, 10,    0x0003)
        MAG_TEMPCO_9_8      = get_masked_value(data, 8,     0x0003)
        RESERVED_7          = get_masked_value(data, 7,     0x0001)
        OPERATING_MODE_6_4  = get_masked_value(data, 4,     0x0007)
        T_CH_EN_3           = get_masked_value(data, 3,     0x0001)
        T_RATE_2            = get_masked_value(data, 2,     0x0001)
        T_HLT_EN_1          = get_masked_value(data, 1,     0x0001)
        RESERVED_0          = get_masked_value(data, 0,     0x0003)
        return    \
f"[15] RESERVED: {int_to_hex_string(RESERVED_15)}, \
[14-12] CONV_AVG: {int_to_hex_string(CONV_AVG_14_12)}, \
[11-10] RESERVED: {int_to_hex_string(RESERVED_11_10)}, \
[9-8] MAG_TEMPCO: {int_to_hex_string(MAG_TEMPCO_9_8)}, \
[7] RESERVED: {int_to_hex_string(RESERVED_7)}, \
[6-4] OPERATING_MODE: {int_to_hex_string(OPERATING_MODE_6_4)}, \
[3] T_CH_EN: {int_to_hex_string(T_CH_EN_3)}, \
[2] T_RATE: {int_to_hex_string(T_RATE_2)}, \
[1] T_HLT_EN: {int_to_hex_string(T_HLT_EN_1)}, \
[0] RESERVED: {int_to_hex_string(RESERVED_0)}"

    @staticmethod
    def __CONV_STATUS_DecodingFunction(data: int):
        RESERVED_15_14  = get_masked_value(data, 14,    0x0003)
        RDY_13          = get_masked_value(data, 13,    0x0001)
        A_12            = get_masked_value(data, 12,    0x0001)
        T_11            = get_masked_value(data, 11,    0x0001)
        Z_10            = get_masked_value(data, 10,    0x0001)
        Y_9             = get_masked_value(data, 9,     0x0001)
        X_8             = get_masked_value(data, 8,     0x0001)
        RESERVED_7      = get_masked_value(data, 7,     0x0001)
        SET_COUNT_6_4   = get_masked_value(data, 4,     0x0007)
        RESERVED_3_2    = get_masked_value(data, 2,     0x0003)
        ALRT_STATUS_1_0 = get_masked_value(data, 0,     0x0003)
        return    \
f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
[13] RDY: {int_to_hex_string(RDY_13)}, \
[12] A: {int_to_hex_string(A_12)}, \
[11] T: {int_to_hex_string(T_11)}, \
[10] Z: {int_to_hex_string(Z_10)}, \
[9] Y: {int_to_hex_string(Y_9)}, \
[8] X: {int_to_hex_string(X_8)}, \
[7] RESERVED: {int_to_hex_string(RESERVED_7)}, \
[6-4] SET_COUNT: {int_to_hex_string(SET_COUNT_6_4)}, \
[3-2] RESERVED: {int_to_hex_string(RESERVED_3_2)}, \
[1-0] ALRT_STATUS: {int_to_hex_string(ALRT_STATUS_1_0)}"

    @staticmethod
    def __X_THRX_CONFIG_DecodingFunction(data: int):
        X_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        X_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] X_HI_THRESHOLD: {X_HI_THRESHOLD_15_8}, [7-0] X_LO_THRESHOLD: {X_LO_THRESHOLD_7_0}"

    @staticmethod
    def __Y_THRX_CONFIG_DecodingFunction(data: int):
        Y_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        Y_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] Y_HI_THRESHOLD: {Y_HI_THRESHOLD_15_8}, [7-0] Y_LO_THRESHOLD: {Y_LO_THRESHOLD_7_0}"

    @staticmethod
    def __Z_THRX_CONFIG_DecodingFunction(data: int):
        Z_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        Z_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] Z_HI_THRESHOLD: {Z_HI_THRESHOLD_15_8}, [7-0] Z_LO_THRESHOLD: {Z_LO_THRESHOLD_7_0}"

    @staticmethod
    def __T_THRX_CONFIG_DecodingFunction(data: int):
        T_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        T_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] T_HI_THRESHOLD: {T_HI_THRESHOLD_15_8}, [7-0] T_LO_THRESHOLD: {T_LO_THRESHOLD_7_0}"

    @staticmethod
    def convert_raw_magnetic_field_to_miliTeslas(mag_raw: int, data_type : DataType, Br_range: Br_range)->str:
        if Br_range in tmga5170_frame_decoder.Br_range_mapping:
            Br = tmga5170_frame_decoder.Br_range_mapping[Br_range]
            if data_type == tmga5170_frame_decoder.DataType.default_32bit_access:
                magnetic_field = (mag_raw * 2 * Br)/(2^16)

            else:
                magnetic_field = (mag_raw * 2 * Br)/(2^12)
            magnetic_field_str = f"[{magnetic_field:.2f} mT]"
        else:
            magnetic_field_str = ""
        return magnetic_field_str

    def __X_CH_RESULT_DecodingFunction(self, data: int):

        int_val = uint16_to_int16(data)
        magnetic_field_str = tmga5170_frame_decoder.convert_raw_magnetic_field_to_miliTeslas(int_val, tmga5170_frame_decoder.DataType.default_32bit_access, self.Br_X_axis_enum)
        return f"[15-0] X_CH_RESULT: {int_val} {magnetic_field_str}"

    def __Y_CH_RESULT_DecodingFunction(self, data: int):

        int_val = uint16_to_int16(data)
        magnetic_field_str = tmga5170_frame_decoder.convert_raw_magnetic_field_to_miliTeslas(int_val, tmga5170_frame_decoder.DataType.default_32bit_access, self.Br_Y_axis_enum)
        return f"[15-0] Y_CH_RESULT: {int_val} {magnetic_field_str}"

    def __Z_CH_RESULT_DecodingFunction(self, data: int):

        int_val = uint16_to_int16(data)
        magnetic_field_str = tmga5170_frame_decoder.convert_raw_magnetic_field_to_miliTeslas(int_val, tmga5170_frame_decoder.DataType.default_32bit_access, self.Br_Z_axis_enum)
        return f"[15-0] Z_CH_RESULT: {int_val} {magnetic_field_str}"
    
    @staticmethod
    def convert_raw_temp_to_celsius(temp_raw: int, data_type : DataType)->float:
        #TYP values are used here
        TadcT0 = 17522
        TadcRes = 60
        TsensT0 = 25
        if data_type == tmga5170_frame_decoder.DataType.default_32bit_access:
            temperature = TsensT0 + ((temp_raw - TadcT0)/TadcRes)

        else:
            temperature = TsensT0 + ((16*(temp_raw - (TadcT0/16)))/TadcRes)
        return temperature
    
    @staticmethod
    def __TEMP_RESULT_DecodingFunction(data: int):
        temperature = tmga5170_frame_decoder.convert_raw_temp_to_celsius(data, tmga5170_frame_decoder.DataType.default_32bit_access)
        return f"[15-0] TEMP_RESULT: {data} [{temperature:.2f} Celsius]"

    @staticmethod
    def __AFE_STATUS_DecodingFunction(data: int):
        CFG_RESET_15    = get_masked_value(data, 15,    0x0001)
        RESERVED_14_13  = get_masked_value(data, 13,    0x0003)
        SENS_STAT_12    = get_masked_value(data, 12,    0x0001)
        TEMP_STAT_11    = get_masked_value(data, 11,    0x0001)
        ZHS_STAT_10     = get_masked_value(data, 10,    0x0001)
        YHS_STAT_9      = get_masked_value(data, 9,     0x0001)
        XHS_STAT_8      = get_masked_value(data, 8,     0x0001)
        RESERVED_7_2    = get_masked_value(data, 7,     0x003F)
        TRIM_STAT_1     = get_masked_value(data, 1,     0x0001)
        LDO_STAT_0      = get_masked_value(data, 0,     0x0001)
        return    \
f"[15] CFG_RESET: {int_to_hex_string(CFG_RESET_15)}, \
[14-13] RESERVED: {int_to_hex_string(RESERVED_14_13)}, \
[12] SENS_STAT: {int_to_hex_string(SENS_STAT_12)}, \
[11] TEMP_STAT: {int_to_hex_string(TEMP_STAT_11)}, \
[10] ZHS_STAT: {int_to_hex_string(ZHS_STAT_10)}, \
[9] YHS_STAT: {int_to_hex_string(YHS_STAT_9)}, \
[8] XHS_STAT: {int_to_hex_string(XHS_STAT_8)}, \
[7-2] RESERVED: {int_to_hex_string(RESERVED_7_2)}, \
[1] TRIM_STAT: {int_to_hex_string(TRIM_STAT_1)}, \
[0] LDO_STAT: {int_to_hex_string(LDO_STAT_0)}"

    @staticmethod
    def __SYS_STATUS_DecodingFunction(data: int):
        ALRT_LVL_15             = get_masked_value(data, 15,    0x0001)
        ALRT_DRV_14             = get_masked_value(data, 14,    0x0001)
        SDO_DRV_13              = get_masked_value(data, 13,    0x0001)
        CRC_STAT_12             = get_masked_value(data, 12,    0x0001)
        FRAME_STAT_11           = get_masked_value(data, 11,    0x0001)
        OPERATING_STAT_10_8     = get_masked_value(data, 8,     0x0007)
        RESERVED_7_6            = get_masked_value(data, 6,     0x0003)
        VCC_OV_5                = get_masked_value(data, 5,     0x0001)
        VCC_UV_4                = get_masked_value(data, 4,     0x0001)
        TEMP_THX_3              = get_masked_value(data, 3,     0x0001)
        ZCH_THX_2               = get_masked_value(data, 2,     0x0001)
        YCH_THX_1               = get_masked_value(data, 1,     0x0001)
        XCH_THX_0               = get_masked_value(data, 0,     0x0001)
        return    \
f"[15] ALRT_LVL: {int_to_hex_string(ALRT_LVL_15)}, \
[14] ALRT_DRV: {int_to_hex_string(ALRT_DRV_14)}, \
[13] SDO_DRV: {int_to_hex_string(SDO_DRV_13)}, \
[12] CRC_STAT: {int_to_hex_string(CRC_STAT_12)}, \
[11] FRAME_STAT: {int_to_hex_string(FRAME_STAT_11)}, \
[10-8] OPERATING_STAT: {int_to_hex_string(OPERATING_STAT_10_8)}, \
[7-6] RESERVED: {int_to_hex_string(RESERVED_7_6)}, \
[5] VCC_OV: {int_to_hex_string(VCC_OV_5)}, \
[4] VCC_UV: {int_to_hex_string(VCC_UV_4)}, \
[3] TEMP_THX: {int_to_hex_string(TEMP_THX_3)}, \
[2] ZCH_THX: {int_to_hex_string(ZCH_THX_2)}, \
[1] YCH_THX: {int_to_hex_string(YCH_THX_1)}, \
[0] XCH_THX: {int_to_hex_string(XCH_THX_0)}"

    @staticmethod
    def convert_raw_angle_to_deg(angle_raw: int, data_type : DataType)->float:

        if data_type == tmga5170_frame_decoder.DataType.default_32bit_access:
            angle_frac = angle_raw & 0x0F
            angle_frac = angle_frac/16
            angle_integer = (angle_raw >> 4) & 0x01FF

        else:
            angle_frac = angle_raw & 0x07
            angle_frac = angle_frac/8
            angle_integer = (angle_raw >> 3) & 0x01FF

        angle = angle_integer + angle_frac
        return angle

    @staticmethod
    def __ANGLE_RESULT_DecodingFunction(data: int):
        angle = tmga5170_frame_decoder.convert_raw_angle_to_deg(data, tmga5170_frame_decoder.DataType.default_32bit_access)
        return f"[15-0] ANGLE_RESULT: {data} [{angle:.2f} Degrees]"

    @staticmethod
    def __TEST_CONFIG_DecodingFunction(data: int):
        RESERVED_15_6   = get_masked_value(data, 6, 0x03FF)
        VER_5_4         = get_masked_value(data, 4, 0x0003)
        RESERVED_3      = get_masked_value(data, 3, 0x0001)
        CRC_DIS_2       = get_masked_value(data, 2, 0x0001)
        OSC_CNT_CTL_1_0 = get_masked_value(data, 0, 0x0003)
        return    \
f"[15-6] RESERVED: {int_to_hex_string(RESERVED_15_6)}, \
[5-4] VER: {int_to_hex_string(VER_5_4)}, \
[3] RESERVED: {int_to_hex_string(RESERVED_3)}, \
[2] CRC_DIS: {int_to_hex_string(CRC_DIS_2)}, \
[1-0] OSC_CNT_CTL: {int_to_hex_string(OSC_CNT_CTL_1_0)}"

    @staticmethod
    def __OSC_MONITOR_DecodingFunction(data: int):
        return f"[15-0] OSC_COUNT: {data}"

    @staticmethod
    def __MAGNITUDE_RESULT_DecodingFunction(data: int):
        return f"[15-0] MAGNITUDE_RESULT: {data}"

    @staticmethod
    def __dummyDecodingFunction(data: int):
        return "Not yet implemented"
    
    @staticmethod
    def get_16_bit_spi_data_tmag5170 (value):
        if(value != None):
            retVal = get_masked_value(value, TMAG5170_16_BIT_SPI_DATA_POSITION, TMAG5170_16_BIT_SPI_DATA_MASK)
        else:
            retVal = None
        return retVal


    def get_register_acronym(self, register_index):
        retString = "Error, not possible index value"
        if register_index in self.__Tmag5170_register_mapping:
            retString = self.__Tmag5170_register_mapping[register_index].Acronym
        return retString
    
    def get_register_decoded_description(self, register_index, data_32_bit_spi):
        retString = "Error, not possible index value"
        if register_index in self.__Tmag5170_register_mapping:
            data_16_bit_spi = self.get_16_bit_spi_data_tmag5170(data_32_bit_spi)
            retString = self.__Tmag5170_register_mapping[register_index].DecodingFunction(data_16_bit_spi)
        return retString

    @staticmethod
    def get_register_index_from_tmag5170_frame (mosi_value):
        if(mosi_value != None):
            value = get_masked_value(mosi_value, REGISTER_ADDR_POSITION, REGISTER_ADDR_MASK)
        else:
            value = None
        return value

    @staticmethod 
    def convert_tmag5170_bytes_to_int (data):
        value = None
        if (len(data) == TMAG5170_SINGLE_FRAME_BYTE_SIZE):
            value = int.from_bytes(data, 'big', signed = False) 
        return value



    def set_mosi_miso_raw_data(self, mosi_raw_data, miso_raw_data):
            self.mosi_value = tmga5170_frame_decoder.convert_tmag5170_bytes_to_int(mosi_raw_data)
            self.miso_value = tmga5170_frame_decoder.convert_tmag5170_bytes_to_int(miso_raw_data)

    @staticmethod
    def convert_uint_to_mosi_miso_str(value: int):
        if value != None:
            str_value = int_to_hex_string(value, 8)
        else:
            str_value = LENGTH_ERROR_TOKEN
        return str_value
        
    def get_mosi_miso_str(self):
        str_mosi_value = tmga5170_frame_decoder.convert_uint_to_mosi_miso_str(self.mosi_value)
        str_miso_value = tmga5170_frame_decoder.convert_uint_to_mosi_miso_str(self.miso_value)
        return  str_mosi_value, str_miso_value

    @staticmethod
    def calculate_tmag5170_crc (data):
        crc_from_bus = None
        crc_status = ""
        crc_calculated = None

        if (data != None):
            crc_from_bus = data & 0x0F
            padded_frame = data & 0xFFFFFFF0
            frame_crc = 0x0F
            for i in reversed(range(32)):
                inv = get_bit(padded_frame, i) ^ get_bit(frame_crc, 3)
                frame_crc_3bit = get_bit(frame_crc, 2)
                frame_crc_2bit = get_bit(frame_crc, 1)
                frame_crc_1bit = get_bit(frame_crc, 0) ^ inv
                frame_crc_0bit = inv
                frame_crc = (set_bit(frame_crc_3bit, 3) |\
                            set_bit(frame_crc_2bit, 2) |\
                            set_bit(frame_crc_1bit, 1) |\
                            set_bit(frame_crc_0bit, 0)) & 0x0F
            crc_calculated = frame_crc
            if crc_calculated == crc_from_bus:
                crc_status = CRC_OK_TOKEN
            else:
                crc_status = CRC_ERROR_TOKEN
        return tmga5170_frame_decoder.crc_4_bit_group_type(crc_status, crc_calculated, crc_from_bus)
    
    @staticmethod
    def retrieve_4_bit_cmd_stat (miso_data, mosi_data):
        cmd3        = None
        cmd2        = None
        cmd1        = None
        cmd0        = None
        error_stat  = None
        stat_2_0    = None

        if (miso_data != None):
            error_stat  = get_bit(mosi_data, 7)
            stat_2_0    = get_masked_value(miso_data, 4, 0x07)

        if (mosi_data != None):
            cmd0        = get_bit(mosi_data, 4)
            cmd1        = get_bit(mosi_data, 5)
            cmd2        = get_bit(mosi_data, 6)
            cmd3        = get_bit(mosi_data, 7)

        return tmga5170_frame_decoder.cmd_stat_4_bit_group_type(cmd3, cmd2, cmd1, cmd0, error_stat, stat_2_0)

    def get_4_bit_crc_cmd_stat_group(self):
        miso_crc_group = tmga5170_frame_decoder.calculate_tmag5170_crc(self.miso_value)
        mosi_crc_group = tmga5170_frame_decoder.calculate_tmag5170_crc(self.mosi_value)
        if self.enable__cmd_stat_4_bit_group == True:
            cmd_stat_4_bit_group = tmga5170_frame_decoder.retrieve_4_bit_cmd_stat(self.miso_value, self.mosi_value)
        else:
            cmd_stat_4_bit_group = tmga5170_frame_decoder.cmd_stat_4_bit_group_type(None, None, None, None, None, None)
        return miso_crc_group, mosi_crc_group, cmd_stat_4_bit_group

    def get_address_8bit_register_16bit_group(self):
        register_address = self.get_register_index_from_tmag5170_frame(self.mosi_value)
        register_name = self.get_register_acronym(register_address)
        if self.mosi_value != None:
            if get_bit(self.mosi_value, READ_WRITE_BIT_POSITION) == 1:
                read_write = READ_REGISTER_TOKEN
                register_value = tmga5170_frame_decoder.get_16_bit_spi_data_tmag5170(self.miso_value)
                register_decoding = self.get_register_decoded_description(register_address, self.miso_value)
            else:
                read_write = WRITE_REGISTER_TOKEN
                register_value = tmga5170_frame_decoder.get_16_bit_spi_data_tmag5170(self.mosi_value)
                register_decoding = self.get_register_decoded_description(register_address, self.mosi_value)
        else:
            read_write = ""
            register_value = None
            register_decoding = ""
        return tmga5170_frame_decoder.address_8bit_register_16bit_group_type(read_write, register_address, register_name, register_decoding, register_value)

    def get_stat_8_bit_group(self):
        prev_crc_stat           = None
        cfg_reset_stat          = None
        sys_alrt_status1_stat   = None
        afe_alrt_status0_stat   = None
        x_stat                  = None
        y_stat                  = None
        z_stat                  = None
        t_stat                  = None

        if self.miso_value != None:
            prev_crc_stat           = get_bit(self.miso_value, 31)
            cfg_reset_stat          = get_bit(self.miso_value, 30)
            sys_alrt_status1_stat   = get_bit(self.miso_value, 29)
            afe_alrt_status0_stat   = get_bit(self.miso_value, 28)
            x_stat                  = get_bit(self.miso_value, 27)
            y_stat                  = get_bit(self.miso_value, 26)
            z_stat                  = get_bit(self.miso_value, 25)
            t_stat                  = get_bit(self.miso_value, 24)

        return tmga5170_frame_decoder.stat_8_bit_group_type(prev_crc_stat, cfg_reset_stat, sys_alrt_status1_stat, afe_alrt_status0_stat, x_stat, y_stat, z_stat, t_stat)

    def get_register_16_bit_address_stat_8_bit_group(self):
        address_8bit_register_16bit_group = self.get_address_8bit_register_16bit_group()
        if self.enable__stat_8_bit_group == True:
            stat_8_bit_group = self.get_stat_8_bit_group()
        else:
            stat_8_bit_group = tmga5170_frame_decoder.stat_8_bit_group_type(None, None, None, None, None, None, None, None)
        return address_8bit_register_16bit_group, stat_8_bit_group
        
    def get_24_bit_data_group(self):
        ch1_value = ""
        ch2_value = ""
        register_address = None
        register_name = ""
        register_decoding = ""
        register_value = None
        read_write = ""

        if self.mosi_value != None:
            if get_bit(self.mosi_value, READ_WRITE_BIT_POSITION) == 1:
                read_write = READ_REGISTER_TOKEN
            else:
                read_write = WRITE_REGISTER_TOKEN
                register_address = self.get_register_index_from_tmag5170_frame(self.mosi_value)
                register_name = self.get_register_acronym(register_address)
                register_value = tmga5170_frame_decoder.get_16_bit_spi_data_tmag5170(self.mosi_value)
                register_decoding = self.get_register_decoded_description(register_address, self.mosi_value)

        if self.miso_value != None:
            first_4_bits_ch1 = get_masked_value(self.miso_value, 8, 0x0F)
            next_8_bits_ch1 = get_masked_value(self.miso_value, 16, 0xFF)
            all_12_bits_ch1 = (next_8_bits_ch1<<8) | first_4_bits_ch1

            first_4_bits_ch2 = get_masked_value(self.miso_value, 12, 0x0F)
            next_8_bits_ch2 = get_masked_value(self.miso_value, 24, 0xFF)
            all_12_bits_ch2 = (next_8_bits_ch2<<8) | first_4_bits_ch2
            if self.data_type == self.DataType.magnetic_field:
                ch1_value = uintX_to_intX_represented_on_Y_bytes(all_12_bits_ch1, 12, 2)
                ch2_value = uintX_to_intX_represented_on_Y_bytes(all_12_bits_ch2, 12, 2)

            elif self.data_type == self.DataType.magnetic_field_temperature:
                ch1_value = uintX_to_intX_represented_on_Y_bytes(all_12_bits_ch1, 12, 2)
                ch2_value = all_12_bits_ch2

            elif self.data_type == self.DataType.angle_magnitude:
                ch1_value = all_12_bits_ch1
                ch2_value = all_12_bits_ch2

            else:
                ch1_value = None
                ch2_value = None



        return tmga5170_frame_decoder.data_24_bit_group_type(read_write, ch1_value, ch2_value, register_address, register_name, register_decoding, register_value)
# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):

    DATA_TYPE_MAGNETIC_FIELD_ONLY_STRING = "DATA_TYPE = 1h-3h, 12-Bit XY/XZ/ZY data access"
    DATA_TYPE_MAGNETIC_FIELD_AND_TEMPERATURE_STRING = "DATA_TYPE = 4h-6h, 12-Bit XT/YT/ZT data access"
    DATA_TYPE_ANGLE_AND_MAGNITUDE_STRING = "DATA_TYPE = 7h, 12-Bit AM data access"
    DATA_TYPE_EQUAL_O_STRING = "DATA_TYPE = 0h, Default 32-bit register access"
    #Only data type to which I have data is 0x00h due that others data_type are currently not implemented
    DATA_TYPE = ChoicesSetting(choices=(DATA_TYPE_EQUAL_O_STRING, DATA_TYPE_MAGNETIC_FIELD_ONLY_STRING, DATA_TYPE_MAGNETIC_FIELD_AND_TEMPERATURE_STRING, DATA_TYPE_ANGLE_AND_MAGNITUDE_STRING))

    CRC_EN_STRING = "CRC_DIS = 0h, CRC enabled in SPI communication"
    CRC_DIS_STRING = "CRC_DIS = 1h, CRC disabled in SPI communication"
    #Disabling crc is lifting FRAME_STAT check due to lack of data how frames looks in this type I am not implementing this feature
    CRC_DIS = ChoicesSetting(choices=(CRC_EN_STRING,CRC_DIS_STRING))


    A1_50MT = "±50mT (TMAG5170A1)"
    A1_25MT = "±25mT (TMAG5170A1)"
    A1_100MT = "±100mT (TMAG5170A1)"

    A2_150MT = "±150mT (TMAG5170A2)"
    A2_75MT = "±75mT (TMAG5170A2)"
    A2_300MT = "±300mT (TMAG5170A2)"

    RANGE_NOT_SELECTED = "-"

    X_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))
    Y_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))
    Z_RANGE = ChoicesSetting(choices=(RANGE_NOT_SELECTED, A2_150MT, A2_75MT, A2_300MT, A1_50MT, A1_25MT, A1_100MT))

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'tmag5170_regular': {
            'format': \
            'MOSI:{{data.mosi_frame}}, \
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            crc_mosi_from_bus: {{data.mosi_crc_from_bus}},\
            {{data.crc_mosi_correct}}, \
            \nMISO:{{data.miso_frame}}, \
            crc_miso_expected: {{data.miso_crc_calculated}}, \
            crc_miso_from_bus: {{data.miso_crc_from_bus}}, \
            {{data.crc_miso_correct}}, \
            R/W:{{data.read_write}}, \
            RegAddr:{{data.register_address}} - {{data.register_name}}, \
            reg_val:{{data.register_value}}, \
            decoded_reg_val:{{data.register_decoding}}, \
            FrameCnt_debug:{{data.FrameCnt_debug}}'\
        },
        'tmag5170_special': {
            'format': \
            'MOSI:{{data.mosi_frame}}, \
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            crc_mosi_from_bus: {{data.mosi_crc_from_bus}},\
            {{data.crc_mosi_correct}}, \
            \nMISO:{{data.miso_frame}}, \
            crc_miso_expected: {{data.miso_crc_calculated}}, \
            crc_miso_from_bus: {{data.miso_crc_from_bus}}, \
            {{data.crc_miso_correct}}, \
            ch1_value:{{data.ch1_value}}, \
            ch2_value:{{data.ch2_value}}, \
            R/W:{{data.read_write}}, \
            RegAddr:{{data.register_address}} - {{data.register_name}}, \
            reg_val:{{data.register_value}}, \
            decoded_reg_val:{{data.register_decoding}}, \
            FrameCnt_debug:{{data.FrameCnt_debug}}'\
        }
    }
    
    

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        if self.DATA_TYPE == self.DATA_TYPE_EQUAL_O_STRING:
            data_type_var = tmga5170_frame_decoder.DataType.default_32bit_access

        elif self.DATA_TYPE == self.DATA_TYPE_MAGNETIC_FIELD_ONLY_STRING:
            data_type_var = tmga5170_frame_decoder.DataType.magnetic_field

        elif self.DATA_TYPE == self.DATA_TYPE_MAGNETIC_FIELD_AND_TEMPERATURE_STRING:
            data_type_var = tmga5170_frame_decoder.DataType.magnetic_field_temperature

        elif self.DATA_TYPE == self.DATA_TYPE_ANGLE_AND_MAGNITUDE_STRING:
            data_type_var = tmga5170_frame_decoder.DataType.angle_magnitude

        else:
            raise Exception("Incorrect DATA_TYPE settings") 




        self.decoder = tmga5170_frame_decoder(data_type = data_type_var)
        print("Settings:", self.DATA_TYPE,
              self.CRC_DIS)

        self.frame_data_MISO = bytearray(b'')
        self.frame_data_MOSI = bytearray(b'')
        self.start_frame_label_time = None
        self.end_frame_label_time = None
        self.counter = 0

    def generateAnalyzerFrame(self):

            mosi_frame, miso_frame = self.decoder.get_mosi_miso_str()
            miso_crc_group, mosi_crc_group, cmd_stat_4_bit_group = self.decoder.get_4_bit_crc_cmd_stat_group()

            if self.DATA_TYPE == self.DATA_TYPE_EQUAL_O_STRING:
                address_8bit_register_16bit_group, stat_8_bit_group = self.decoder.get_register_16_bit_address_stat_8_bit_group()
                read_write = address_8bit_register_16bit_group.read_write
                register_name = address_8bit_register_16bit_group.register_name

                AnalyzerFrameType = 'tmag5170_regular'
                AnalyzerFrameDictionary = {\
                        'mosi_frame':mosi_frame,                                                                            \
                        'mosi_crc_calculated':int_to_hex_string(mosi_crc_group.crc_calculated),                             \
                        'mosi_crc_from_bus':int_to_hex_string(mosi_crc_group.crc_from_bus),                                 \
                        'crc_mosi_correct':mosi_crc_group.crc_status,                                                       \
                        'miso_frame':miso_frame,                                                                            \
                        'miso_crc_calculated':int_to_hex_string(miso_crc_group.crc_calculated),                             \
                        'miso_crc_from_bus':int_to_hex_string(miso_crc_group.crc_from_bus),                                 \
                        'crc_miso_correct':miso_crc_group.crc_status,                                                       \
                        'read_write':read_write,                                                                            \
                        'register_address':int_to_hex_string(address_8bit_register_16bit_group.register_address),           \
                        'register_name':register_name,                                                                      \
                        'register_value':int_to_hex_string(address_8bit_register_16bit_group.register_value, 4),            \
                        'register_decoding':address_8bit_register_16bit_group.register_decoding,                            \
                        'stat_2_0':int_to_hex_string(cmd_stat_4_bit_group.stat_2_0),                                        \
                        'error_stat':int_to_hex_string(cmd_stat_4_bit_group.error_stat),                                    \
                        't_stat':int_to_hex_string(stat_8_bit_group.t_stat),                                                \
                        'z_stat':int_to_hex_string(stat_8_bit_group.z_stat),                                                \
                        'y_stat':int_to_hex_string(stat_8_bit_group.y_stat),                                                \
                        'x_stat':int_to_hex_string(stat_8_bit_group.x_stat),                                                \
                        'afe_alrt_status0_stat':int_to_hex_string(stat_8_bit_group.afe_alrt_status0_stat),                  \
                        'sys_alrt_status1_stat':int_to_hex_string(stat_8_bit_group.sys_alrt_status1_stat),                  \
                        'cfg_reset_stat':int_to_hex_string(stat_8_bit_group.cfg_reset_stat),                                \
                        'prev_crc_stat':int_to_hex_string(stat_8_bit_group.prev_crc_stat),                                  \
                        'cmd3':int_to_hex_string(cmd_stat_4_bit_group.cmd3),                                                \
                        'cmd2':int_to_hex_string(cmd_stat_4_bit_group.cmd2),                                                \
                        'cmd1':int_to_hex_string(cmd_stat_4_bit_group.cmd1),                                                \
                        'cmd0':int_to_hex_string(cmd_stat_4_bit_group.cmd0),                                                \
                        'FrameCnt_debug':self.counter,                                                                      \
                }
                
            else:
                data_24_bit_group = self.decoder.get_24_bit_data_group()
                read_write = data_24_bit_group.read_write
                register_name = data_24_bit_group.register_name

                AnalyzerFrameType = 'tmag5170_special'
                AnalyzerFrameDictionary = {\
                        'mosi_frame':mosi_frame,                                                                            \
                        'mosi_crc_calculated':int_to_hex_string(mosi_crc_group.crc_calculated),                             \
                        'mosi_crc_from_bus':int_to_hex_string(mosi_crc_group.crc_from_bus),                                 \
                        'crc_mosi_correct':mosi_crc_group.crc_status,                                                       \
                        'miso_frame':miso_frame,                                                                            \
                        'miso_crc_calculated':int_to_hex_string(miso_crc_group.crc_calculated),                             \
                        'miso_crc_from_bus':int_to_hex_string(miso_crc_group.crc_from_bus),                                 \
                        'crc_miso_correct':miso_crc_group.crc_status,                                                       \
                        'read_write':read_write,                                                                            \
                        'register_address':int_to_hex_string(data_24_bit_group.register_address),                           \
                        'register_name':register_name,                                                                      \
                        'register_value':int_to_hex_string(data_24_bit_group.register_value, 4),                            \
                        'register_decoding':data_24_bit_group.register_decoding,                                            \
                        'ch1_value':data_24_bit_group.ch1_value,                                                            \
                        'ch2_value':data_24_bit_group.ch2_value,                                                            \
                        'stat_2_0':int_to_hex_string(cmd_stat_4_bit_group.stat_2_0),                                        \
                        'error_stat':int_to_hex_string(cmd_stat_4_bit_group.error_stat),                                    \
                        'cmd3':int_to_hex_string(cmd_stat_4_bit_group.cmd3),                                                \
                        'cmd2':int_to_hex_string(cmd_stat_4_bit_group.cmd2),                                                \
                        'cmd1':int_to_hex_string(cmd_stat_4_bit_group.cmd1),                                                \
                        'cmd0':int_to_hex_string(cmd_stat_4_bit_group.cmd0),                                                \
                        'FrameCnt_debug':self.counter,                                                                      \
                }
            retVal = AnalyzerFrame(AnalyzerFrameType, self.start_frame_label_time, self.end_frame_label_time, AnalyzerFrameDictionary)
            print(f"FrameCnt_debug: {self.counter: >6}, mosi_f: {mosi_frame: >10}, crc_mosi: {mosi_crc_group.crc_status: >{len(CRC_ERROR_TOKEN)}}, miso_f: {miso_frame: >10}, crc_miso: {miso_crc_group.crc_status: >{len(CRC_ERROR_TOKEN)}}, read_write: {read_write: >6} reg name:{register_name}")
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
            self.decoder.set_mosi_miso_raw_data(self.frame_data_MOSI, self.frame_data_MISO)
            retVal = self.generateAnalyzerFrame()


        if(frame.type == "result"):
            if self.CRC_DIS == self.CRC_DIS_STRING:
                if (len(self.frame_data_MISO) == TMAG5170_SINGLE_FRAME_BYTE_SIZE) or (len(self.frame_data_MOSI) == TMAG5170_SINGLE_FRAME_BYTE_SIZE):
                    self.end_frame_label_time = frame.start_time
                    retVal = self.generateAnalyzerFrame()
                    self.start_frame_label_time = frame.start_time

            self.frame_data_MISO += frame.data['miso']
            self.frame_data_MOSI += frame.data['mosi']

        # Return the data frame itself
        return retVal

