import uBitSN01 as s
import utime

my_gps=s.MicropyGPS()

while True:
    print(my_gps.latitude())
    print(my_gps.longitude())
    utime.sleep(1)
