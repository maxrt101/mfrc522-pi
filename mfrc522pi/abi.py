
class PCD:
    IDLE       = 0x00
    AUTHENT    = 0x0E
    RECEIVE    = 0x08
    TRANSMIT   = 0x04
    TRANSCEIVE = 0x0C
    RESETPHASE = 0x0F
    CALCCRC    = 0x03

class PICC:
    REQIDL    = 0x26
    REQALL    = 0x52
    ANTICOLL  = 0x93
    SElECTTAG = 0x93
    AUTHENT1A = 0x60
    AUTHENT1B = 0x61
    READ      = 0x30
    WRITE     = 0xA0
    DECREMENT = 0xC0
    INCREMENT = 0xC1
    RESTORE   = 0xC2
    TRANSFER  = 0xB0
    HALT      = 0x50

class MI:
    OK       = 0
    NOTAGERR = 1
    ERR      = 2

class REG:
    Reserved00     = 0x00
    Command        = 0x01
    CommIEn        = 0x02
    DivlEn         = 0x03
    CommIrq        = 0x04
    DivIrq         = 0x05
    Error          = 0x06
    Status1        = 0x07
    Status2        = 0x08
    FIFOData       = 0x09
    FIFOLevel      = 0x0A
    WaterLevel     = 0x0B
    Control        = 0x0C
    BitFraming     = 0x0D
    Coll           = 0x0E
    Reserved01     = 0x0F

    Reserved10     = 0x10
    Mode           = 0x11
    TxMode         = 0x12
    RxMode         = 0x13
    TxControl      = 0x14
    TxAuto         = 0x15
    TxSel          = 0x16
    RxSel          = 0x17
    RxThreshold    = 0x18
    Demod          = 0x19
    Reserved11     = 0x1A
    Reserved12     = 0x1B
    Mifare         = 0x1C
    Reserved13     = 0x1D
    Reserved14     = 0x1E
    SerialSpeed    = 0x1F

    Reserved20     = 0x20
    CRCResultM     = 0x21
    CRCResultL     = 0x22
    Reserved21     = 0x23
    ModWidth       = 0x24
    Reserved22     = 0x25
    RFCfg          = 0x26
    GsN            = 0x27
    CWGsP          = 0x28
    ModGsP         = 0x29
    TMode          = 0x2A
    TPrescaler     = 0x2B
    TReloadH       = 0x2C
    TReloadL       = 0x2D
    TCounterValueH = 0x2E
    TCounterValueL = 0x2F

    Reserved30     = 0x30
    TestSel1       = 0x31
    TestSel2       = 0x32
    TestPinEn      = 0x33
    TestPinValue   = 0x34
    TestBus        = 0x35
    AutoTest       = 0x36
    Version        = 0x37
    AnalogTest     = 0x38
    TestDAC1       = 0x39
    TestDAC2       = 0x3A
    TestADC        = 0x3B
    Reserved31     = 0x3C
    Reserved32     = 0x3D
    Reserved33     = 0x3E
    Reserved34     = 0x3F
