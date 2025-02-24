# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
import collections

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

def uintX_to_intX_represented_on_8_bits (in_value: int, size_of_in_value: int) -> int:
    int_val = None
    if size_of_in_value <= 8 and size_of_in_value>0:
        value = in_value
        sign_bit = get_bit(in_value, size_of_in_value - 1)
        for i in range((size_of_in_value),8):
            value = set_bit_in_value(sign_bit, i, value)
        byte_value = value.to_bytes(1, 'big')
        int_val = int.from_bytes(byte_value, 'big', signed = True)
    return (int_val)

def int_to_hex_string(value:int):
    if value == None:
        return ""
    else:
        return hex(value).upper().replace('X', 'x')
class tmga5170_frame_decoder:
    def __init__(self):
        self.__tmag5170_mapping_type = collections.namedtuple('__tmag5170_mapping_type', ['Acronym', 'DecodingFunction'])
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


    def __MAG_OFFSET_CONFIG_DecodingFunction(self, data: int):
        OFFSET_SELECTION_15_14 = get_masked_value(data, 14,    0x0003)
        OFFSET_VALUE1__13_7    = get_masked_value(data, 7,    0x007F)
        OFFSET_VALUE2__6_0     = get_masked_value(data, 0,    0x007F)
        return    f"[15-14] OFFSET_SELECTION: {int_to_hex_string(OFFSET_SELECTION_15_14)}, \
                    [13-7] OFFSET_VALUE1: {uintX_to_intX_represented_on_8_bits(OFFSET_VALUE1__13_7, 7)}, \
                    [6-0] OFFSET_VALUE2: {uintX_to_intX_represented_on_8_bits(OFFSET_VALUE2__6_0, 7)}"

    def __MAG_GAIN_CONFIG_DecodingFunction(self, data: int):
        GAIN_SELECTION_15_14 = get_masked_value(data, 14,    0x0003)
        RESERVED_13_11       = get_masked_value(data, 11,    0x0007)
        GAIN_VALUE_10_0      = get_masked_value(data, 10,    0x07FF)
        return    f"[15-14] GAIN_SELECTION: {int_to_hex_string(GAIN_SELECTION_15_14)}, \
                    [13-11] RESERVED: {int_to_hex_string(RESERVED_13_11)}, \
                    [10-0] GAIN_VALUE: {int_to_hex_string(GAIN_VALUE_10_0)}"

    def __ALERT_CONFIG_DecodingFunction(self, data: int):
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
        return    f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
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

    def __SYSTEM_CONFIG_DecodingFunction(self, data: int):
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
        return    f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
                    [13-12] DIAG_SEL: {int_to_hex_string(DIAG_SEL_13_12)}, \
                    [11] RESERVED: {int_to_hex_string(RESERVED_11)}, \
                    [10-9] TRIGGER_MODE: {int_to_hex_string(TRIGGER_MODE_10_9)}, \
                    [8-6] DATA_TYPE: {int_to_hex_string(DATA_TYPE_8_6)}, \
                    [5] DIAG_EN: {int_to_hex_string(DIAG_EN_5)}, \
                    [4-3] RESERVED: {int_to_hex_string(RESERVED_4_3)}, \
                    [2] Z_HLT_EN: {int_to_hex_string(Z_HLT_EN_2)}, \
                    [1] Y_HLT_EN: {int_to_hex_string(Y_HLT_EN_1)}, \
                    [0] X_HLT_EN: {int_to_hex_string(X_HLT_EN_0)}"

    def __SENSOR_CONFIG_DecodingFunction(self, data: int):
        ANGLE_EN_15_14      = get_masked_value(data, 14,    0x0003)
        SLEEPTIME_13_10     = get_masked_value(data, 10,    0x000F)
        MAG_CH_EN_9_6       = get_masked_value(data, 6,     0x000F)
        Z_RANGE_5_4         = get_masked_value(data, 4,     0x0003)
        Y_RANGE_3_2         = get_masked_value(data, 2,     0x0003)
        X_RANGE_1_0         = get_masked_value(data, 0,     0x0003)
        return    f"[15-14] ANGLE_EN: {int_to_hex_string(ANGLE_EN_15_14)}, \
                    [13-10] SLEEPTIME: {int_to_hex_string(SLEEPTIME_13_10)}, \
                    [9-6] MAG_CH_EN: {int_to_hex_string(MAG_CH_EN_9_6)}, \
                    [5-4] Z_RANGE: {int_to_hex_string(Z_RANGE_5_4)}, \
                    [3-2] Y_RANGE: {int_to_hex_string(Y_RANGE_3_2)}, \
                    [1-0] X_RANGE: {int_to_hex_string(X_RANGE_1_0)}"

    def __DEVICE_CONFIG_DecodingFunction(self, data: int):
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
        return    f"[15] RESERVED: {int_to_hex_string(RESERVED_15)}, \
                    [14-12] CONV_AVG: {int_to_hex_string(CONV_AVG_14_12)}, \
                    [11-10] RESERVED: {int_to_hex_string(RESERVED_11_10)}, \
                    [9-8] MAG_TEMPCO: {int_to_hex_string(MAG_TEMPCO_9_8)}, \
                    [7] RESERVED: {int_to_hex_string(RESERVED_7)}, \
                    [6-4] OPERATING_MODE: {int_to_hex_string(OPERATING_MODE_6_4)}, \
                    [3] T_CH_EN: {int_to_hex_string(T_CH_EN_3)}, \
                    [2] T_RATE: {int_to_hex_string(T_RATE_2)}, \
                    [1] T_HLT_EN: {int_to_hex_string(T_HLT_EN_1)}, \
                    [0] RESERVED: {int_to_hex_string(RESERVED_0)}"

    def __CONV_STATUS_DecodingFunction(self, data: int):
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
        return    f"[15-14] RESERVED: {int_to_hex_string(RESERVED_15_14)}, \
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

    def __X_THRX_CONFIG_DecodingFunction(self, data: int):
        X_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        X_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] X_HI_THRESHOLD: {X_HI_THRESHOLD_15_8}, [7-0] X_LO_THRESHOLD: {X_LO_THRESHOLD_7_0}"
    
    def __Y_THRX_CONFIG_DecodingFunction(self, data: int):
        Y_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        Y_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] Y_HI_THRESHOLD: {Y_HI_THRESHOLD_15_8}, [7-0] Y_LO_THRESHOLD: {Y_LO_THRESHOLD_7_0}"
    
    def __Z_THRX_CONFIG_DecodingFunction(self, data: int):
        Z_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        Z_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] Z_HI_THRESHOLD: {Z_HI_THRESHOLD_15_8}, [7-0] Z_LO_THRESHOLD: {Z_LO_THRESHOLD_7_0}"
    
    def __T_THRX_CONFIG_DecodingFunction(self, data: int):
        T_HI_THRESHOLD_15_8 = uint8_to_int8(get_masked_value(data, 8, 0xFF))
        T_LO_THRESHOLD_7_0  = uint8_to_int8(get_masked_value(data, 0, 0xFF))
        return f"[15-8] T_HI_THRESHOLD: {T_HI_THRESHOLD_15_8}, [7-0] T_LO_THRESHOLD: {T_LO_THRESHOLD_7_0}"

    def __X_CH_RESULT_DecodingFunction(self, data: int):
        int_val = uint16_to_int16(data)
        return f"[15-0] X_CH_RESULT: {int_val}"

    def __Y_CH_RESULT_DecodingFunction(self, data: int):
        int_val = uint16_to_int16(data)
        return f"[15-0] Y_CH_RESULT: {int_val}"

    def __Z_CH_RESULT_DecodingFunction(self, data: int):
        int_val = uint16_to_int16(data)
        return f"[15-0] Z_CH_RESULT: {int_val}"

    def __TEMP_RESULT_DecodingFunction(self, data: int):
        return f"[15-0] TEMP_RESULT: {data}"

    def __AFE_STATUS_DecodingFunction(self, data: int):
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
        return    f"[15] CFG_RESET: {int_to_hex_string(CFG_RESET_15)}, \
                    [14-13] RESERVED: {int_to_hex_string(RESERVED_14_13)}, \
                    [12] SENS_STAT: {int_to_hex_string(SENS_STAT_12)}, \
                    [11] TEMP_STAT: {int_to_hex_string(TEMP_STAT_11)}, \
                    [10] ZHS_STAT: {int_to_hex_string(ZHS_STAT_10)}, \
                    [9] YHS_STAT: {int_to_hex_string(YHS_STAT_9)}, \
                    [8] XHS_STAT: {int_to_hex_string(XHS_STAT_8)}, \
                    [7-2] RESERVED: {int_to_hex_string(RESERVED_7_2)}, \
                    [1] TRIM_STAT: {int_to_hex_string(TRIM_STAT_1)}, \
                    [0] LDO_STAT: {int_to_hex_string(LDO_STAT_0)}"

    def __SYS_STATUS_DecodingFunction(self, data: int):
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
        return    f"[15] ALRT_LVL: {int_to_hex_string(ALRT_LVL_15)}, \
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

    def __ANGLE_RESULT_DecodingFunction(self, data: int):
        return f"[15-0] ANGLE_RESULT: {data}"


    def __TEST_CONFIG_DecodingFunction(self, data: int):
        RESERVED_15_6   = get_masked_value(data, 6, 0x03FF)
        VER_5_4         = get_masked_value(data, 4, 0x0003)
        RESERVED_3      = get_masked_value(data, 3, 0x0001)
        CRC_DIS_2       = get_masked_value(data, 2, 0x0001)
        OSC_CNT_CTL_1_0 = get_masked_value(data, 0, 0x0003)
        return    f"[15-6] RESERVED: {int_to_hex_string(RESERVED_15_6)}, \
                    [5-4] VER: {int_to_hex_string(VER_5_4)}, \
                    [3] RESERVED: {int_to_hex_string(RESERVED_3)}, \
                    [2] CRC_DIS: {int_to_hex_string(CRC_DIS_2)}, \
                    [1-0] OSC_CNT_CTL: {int_to_hex_string(OSC_CNT_CTL_1_0)}"
    
    def __OSC_MONITOR_DecodingFunction(self, data: int):
        return f"[15-0] OSC_COUNT: {data}"

    def __MAGNITUDE_RESULT_DecodingFunction(self, data: int):
        return f"[15-0] MAGNITUDE_RESULT: {data}"

    def __dummyDecodingFunction(self, data: int):
        return "Not yet implemented"
    
    def get_16_bit_spi_data_tmag5170 (self, value: int) -> int:
        return get_masked_value(value, TMAG5170_16_BIT_SPI_DATA_POSITION, TMAG5170_16_BIT_SPI_DATA_MASK)
        
    def get_register_acronym(self, register_index: int):
        return self.__Tmag5170_register_mapping[register_index].Acronym
    
    def get_register_decoded_description(self, register_index: int, data_32_bit_spi: int):
        data_16_bit_spi = self.get_16_bit_spi_data_tmag5170(data_32_bit_spi)
        return self.__Tmag5170_register_mapping[register_index].DecodingFunction(data_16_bit_spi)

    def get_register_index_from_tmag5170_frame (self, mosi_value: int) -> int:
        return get_masked_value(mosi_value, REGISTER_ADDR_POSITION, REGISTER_ADDR_MASK)
        
    def convert_tmag5170_bytes_to_int (self, data, start_position: int) -> int:
        value = None
        length = len(data)
        if ((length - start_position) >= TMAG5170_SINGLE_FRAME_BYTE_SIZE):
            print("data")
            print(data)

            data_sliced = data[start_position:(start_position + TMAG5170_SINGLE_FRAME_BYTE_SIZE)]
            print("data_sliced")
            print(data_sliced)
            data_joined = b''.join(data_sliced)
            value = int.from_bytes(data_joined, 'big', signed = False) 
        return value

    def calculate_tmag5170_crc (self, data: int):
        crc_calculated = None
        crc_from_bus = None
        crc_status = None

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
        return crc_calculated, crc_from_bus, crc_status
    







# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):

    #Only data type to which I have data is 0x00h due that others data_type are currently not implemented
    DATA_TYPE = ChoicesSetting(choices=("0h = Default 32-bit register access",))

    #Disabling crc is lifting FRAME_STAT check due to lack of data how frames looks in this type I am not implementing this feature
    CRC_DIS = ChoicesSetting(choices=("0h = CRC enabled in SPI communication",))

    #Disabling crc is lifting FRAME_STAT check due to lack of data how frames looks in this type I am not implementing this feature
    CONV_AVG = ChoicesSetting(choices=("CONV_AVG != 0h, Note: X, Y, Z ch result is represented as 16 bits INT", "0h = 1x - 10.0Ksps (3-axes) or 20Ksps (1 axis), Note: X, Y, Z ch result is represented as 12 bits INT", ))
    enable_time = None
    disable_time = None
    frame_data_MISO = []
    frame_data_MOSI = []

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'tmag5170': {
            'format': \
            'MOSI:{{data.mosi}}, \
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            {{data.crc_mosi_correct}}, \
            R/W:{{data.read_write}}, \
            RegAddr:{{data.register_address}} - {{data.register_name}}, \
            \nMISO:{{data.miso}}, \
            crc_miso_expected: {{data.miso_crc_calculated}},\
            {{data.crc_miso_correct}},\
            decoded_reg_val:{{data.register_decoding}}'
        }
    }
    
    decoder = tmga5170_frame_decoder()

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        print("Settings:", self.DATA_TYPE,
              self.CRC_DIS)


    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''
        crc_mosi_correct = ""
        crc_miso_correct = ""
        read_write = ""
        register_address = None
        register_name = ""
        register_decoding = ""
        mosi_crc_calculated = None
        miso_crc_calculated = None

        if(frame.type == "enable"):
            print("Enable start time " + str(frame.start_time))
            self.enable_time = frame.start_time
        if(frame.type == "disable"):
            print("Disable stop time " + str(frame.end_time))
            self.disable_time = frame.start_time
            print(str(self.frame_data_MOSI))

            if(len(self.frame_data_MOSI) == TMAG5170_SINGLE_FRAME_BYTE_SIZE):
                MOSI  = "0x"
                mosi_value = self.decoder.convert_tmag5170_bytes_to_int(self.frame_data_MOSI, 0)
                mosi_crc_calculated, mosi_crc_from_bus, crc_mosi_correct = self.decoder.calculate_tmag5170_crc(mosi_value)
                register_address = self.decoder.get_register_index_from_tmag5170_frame(mosi_value)
                register_name = self.decoder.get_register_acronym(register_address)

                if get_bit(mosi_value, READ_WRITE_BIT_POSITION) == 1:
                    read_write = READ_REGISTER_TOKEN
                else:
                    read_write = WRITE_REGISTER_TOKEN
                    register_decoding = self.decoder.get_register_decoded_description(register_address, mosi_value)

                for i in self.frame_data_MOSI:
                    MOSI += (i.hex()).upper()
            else:
                MOSI = LENGTH_ERROR_TOKEN
            
            if(len(self.frame_data_MISO) == TMAG5170_SINGLE_FRAME_BYTE_SIZE):
                MISO  = "0x"
                miso_value = self.decoder.convert_tmag5170_bytes_to_int(self.frame_data_MISO, 0)
                miso_crc_calculated, miso_crc_from_bus, crc_miso_correct = self.decoder.calculate_tmag5170_crc(miso_value)

                if read_write == READ_REGISTER_TOKEN:
                    register_decoding = self.decoder.get_register_decoded_description(register_address, miso_value)
                
                for i in self.frame_data_MISO:
                    MISO += (i.hex()).upper()
            else:
                MISO = LENGTH_ERROR_TOKEN
            if(( self.enable_time != None )and( self.disable_time != None )):
                retVal = AnalyzerFrame('tmag5170', self.enable_time, self.disable_time, 
                                       {                                                                                \
                                            'mosi':MOSI,                                                                \
                                            'mosi_crc_calculated':int_to_hex_string(mosi_crc_calculated),               \
                                            'miso':MISO,                                                                \
                                            'miso_crc_calculated':int_to_hex_string(miso_crc_calculated),               \
                                            'crc_miso_correct':crc_miso_correct,                                        \
                                            'crc_mosi_correct':crc_mosi_correct,                                        \
                                            'read_write':read_write,                                                    \
                                            'register_address':int_to_hex_string(register_address),                     \
                                            'register_name':register_name,                                              \
                                            'register_decoding':register_decoding,                                      \
                                        })
            self.disable_time = None
            self.enable_time = None
            self.frame_data_MISO = []
            self.frame_data_MOSI = []
            if(( retVal.start_time != None )and( retVal.end_time != None )):
                return retVal

        if(frame.type == "result"):
            self.frame_data_MISO.append(frame.data['miso'])
            self.frame_data_MOSI.append(frame.data['mosi'])
            print("MISO " + str(frame.data['miso']))
            print("MOSI " + str(frame.data['mosi']))
        print("frame.type " + str(frame.type))
        # Return the data frame itself

