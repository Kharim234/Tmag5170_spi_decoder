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

def uint16_to_int16 (in_value: int) -> int:
    value = in_value.to_bytes(2, 'big')
    int_val = int.from_bytes(value, 'big', signed = True)
    return (int_val)

class tmga5170_frame_decoder:
    def __init__(self):
        self.__tmag5170_mapping_type = collections.namedtuple('__tmag5170_mapping_type', ['Acronym', 'DecodingFunction'])
        self.__Tmag5170_register_mapping = {
            0x00: self.__tmag5170_mapping_type("DEVICE_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x01: self.__tmag5170_mapping_type("SENSOR_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x02: self.__tmag5170_mapping_type("SYSTEM_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x03: self.__tmag5170_mapping_type("ALERT_CONFIG"     ,    self.__dummyDecodingFunction)              ,
            0x04: self.__tmag5170_mapping_type("X_THRX_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x05: self.__tmag5170_mapping_type("Y_THRX_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x06: self.__tmag5170_mapping_type("Z_THRX_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x07: self.__tmag5170_mapping_type("T_THRX_CONFIG"    ,    self.__dummyDecodingFunction)              ,
            0x08: self.__tmag5170_mapping_type("CONV_STATUS"      ,    self.__CONV_STATUS_DecodingFunction)       ,
            0x09: self.__tmag5170_mapping_type("X_CH_RESULT"      ,    self.__X_CH_RESULT_DecodingFunction)       ,
            0x0A: self.__tmag5170_mapping_type("Y_CH_RESULT"      ,    self.__Y_CH_RESULT_DecodingFunction)       ,
            0x0B: self.__tmag5170_mapping_type("Z_CH_RESULT"      ,    self.__Z_CH_RESULT_DecodingFunction)       ,
            0x0C: self.__tmag5170_mapping_type("TEMP_RESULT"      ,    self.__TEMP_RESULT_DecodingFunction)       ,
            0x0D: self.__tmag5170_mapping_type("AFE_STATUS"       ,    self.__AFE_STATUS_DecodingFunction)        ,
            0x0E: self.__tmag5170_mapping_type("SYS_STATUS"       ,    self.__SYS_STATUS_DecodingFunction)        ,
            0x0F: self.__tmag5170_mapping_type("TEST_CONFIG"      ,    self.__TEST_CONFIG_DecodingFunction)       ,
            0x10: self.__tmag5170_mapping_type("OSC_MONITOR"      ,    self.__dummyDecodingFunction)              ,
            0x11: self.__tmag5170_mapping_type("MAG_GAIN_CONFIG"  ,    self.__dummyDecodingFunction)              ,
            0x12: self.__tmag5170_mapping_type("MAG_OFFSET_CONFIG",    self.__dummyDecodingFunction)              ,
            0x13: self.__tmag5170_mapping_type("ANGLE_RESULT"     ,    self.__ANGLE_RESULT_DecodingFunction)      ,
            0x14: self.__tmag5170_mapping_type("MAGNITUDE_RESULT" ,    self.__dummyDecodingFunction)     
        }

    def __CONV_STATUS_DecodingFunction(self, data: int):
        return "Not yet implemented"

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
        return "Not yet implemented"

    def __SYS_STATUS_DecodingFunction(self, data: int):
        return "Not yet implemented"

    def __ANGLE_RESULT_DecodingFunction(self, data: int):
        return f"[15-0] ANGLE_RESULT: {data}"


    def __TEST_CONFIG_DecodingFunction(self, data: int):
        return "Not yet implemented"

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
        'mytype': {
            'format': \
            'MOSI:{{data.mosi}}, \
            crc_mosi_expected: {{data.mosi_crc_calculated}},\
            {{data.crc_mosi_correct}}, \
            R/W:{{data.read_write}}, \
            RegAddr:{{data.register_address}} - {{data.register_name}}, \
            \nMISO:{{data.miso}}, \
            crc_miso_expected: {{data.miso_crc_calculated}},\
            {{data.crc_miso_correct}}'
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
        register_address = 0
        register_name = ""
        register_decoding = ""

        if(frame.type == "enable"):
            print("Enable start time " + str(frame.start_time))
            self.enable_time = frame.start_time
        if(frame.type == "disable"):
            print("Disable stop time " + str(frame.end_time))
            self.disable_time = frame.start_time
            print(str(self.frame_data_MOSI))
            mosi_crc_calculated = 0
            miso_crc_calculated = 0
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
                retVal = AnalyzerFrame('mytype', self.enable_time, self.disable_time, 
                                       {                                                                                \
                                            'mosi':MOSI,                                                                \
                                            'mosi_crc_calculated':hex(mosi_crc_calculated).upper().replace('X', 'x'),   \
                                            'miso':MISO,                                                                \
                                            'miso_crc_calculated':hex(miso_crc_calculated).upper().replace('X', 'x'),   \
                                            'crc_miso_correct':crc_miso_correct,                                        \
                                            'crc_mosi_correct':crc_mosi_correct,                                        \
                                            'register_decoding':register_decoding,                                      \
                                            'read_write':read_write,                                                    \
                                            'register_address':hex(register_address).upper().replace('X', 'x'),         \
                                            'register_name':register_name,                                              \
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

