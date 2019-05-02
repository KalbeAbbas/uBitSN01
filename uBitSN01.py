from microbit import i2c
SN01_ADDR=0x42

class MicropyGPS(object):

    SENTENCE_LIMIT = 90




    def __init__(self, local_offset=0, location_formatting='dd'):

        self.char_count = 0

        self.sentence_active = False

        self.coord_format=location_formatting

        self._latitude = [0,0]

        self._longitude = [0,0]

        
    def latitude(self):

        if self.coord_format == 'dd':

            i2c.write(SN01_ADDR,str(0xFD))
            
            data=i2c.read(SN01_ADDR,2)
            
            temp=((data[0]<<8) | (data[1]))
            
            if(temp>0 and temp<10000):
                
                for x in range(temp):
                    
                    self.update(i2c.read(SN01_ADDR,1))

            decimal_degrees = self._latitude[0] + (self._latitude[1] / 60)

            return [decimal_degrees]


    def longitude(self):

        if self.coord_format == 'dd':

            i2c.write(SN01_ADDR,str(0xFD))
            
            data=i2c.read(SN01_ADDR,2)
            
            temp=((data[0]<<8) | (data[1]))
            
            if(temp>0 and temp<10000):
                
                for x in range(temp):
                    
                    self.update(i2c.read(SN01_ADDR,1))

            decimal_degrees = self._longitude[0] + (self._longitude[1] / 60)

            return [decimal_degrees]

    def gprmc(self):

        if self.gps_segments[2] == 'A': 

            try:

                l_string = self.gps_segments[3]

                lat_degs = int(l_string[0:2])

                lat_mins = float(l_string[2:])

                l_string = self.gps_segments[5]

                lon_degs = int(l_string[0:3])
                
                lon_mins = float(l_string[3:])

            except ValueError:

                return False

            self._latitude = [lat_degs,lat_mins]

            self._longitude = [lon_degs,lon_mins]



        else:

            self._latitude = [0]

            self._longitude = [0]

            self.valid = False



        return True




    def new_sentence(self):

        self.gps_segments = ['']

        self.active_segment = 0

        self.crc_xor = 0

        self.sentence_active = True

        self.process_crc = True

        self.char_count = 0



    def update(self, new_char):


        valid_sentence = False

        ascii_char = ord(new_char)



        if 10 <= ascii_char <= 126:

            self.char_count += 1


            if new_char == '$':

                self.new_sentence()

                return None



            elif self.sentence_active:

                if new_char == '*':

                    self.process_crc = False

                    self.active_segment += 1

                    self.gps_segments.append('')

                    return None

                elif new_char == ',':

                    self.active_segment += 1

                    self.gps_segments.append('')

                else:

                    self.gps_segments[self.active_segment] += new_char

                    if not self.process_crc:



                        if len(self.gps_segments[self.active_segment]) == 2:

                            try:

                                final_crc = int(self.gps_segments[self.active_segment], 16)

                                if self.crc_xor == final_crc:

                                    valid_sentence = True

                                else:

                                    self.crc_fails += 1

                            except ValueError:

                                pass


                if self.process_crc:

                    self.crc_xor ^= ascii_char


                if valid_sentence:

                    self.sentence_active = False



                    if self.gps_segments[0] in self.supported_sentences:

                        if self.supported_sentences[self.gps_segments[0]](self):


                            return self.gps_segments[0]

                if self.char_count > self.SENTENCE_LIMIT:

                    self.sentence_active = False

        return None


    supported_sentences = {'GPRMC': gprmc}
