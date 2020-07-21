#!/usr/bin/python3
"""
This defines the registers accessible via SPI for a tmc5160
"""

def bytesToSigned32(bytearr):
    """
    converts the last 4 bytes of a 5 byte array to a signed integer
    """
    unsigned=(bytearr[1]<<24)+(bytearr[2]<<16)+(bytearr[3]<<8)+bytearr[4]
    return unsigned-4294967296 if bytearr[1]&128 else unsigned

def bytesToSigned24(bytearr):
    """
    converts the last 4 bytes of a 5 byte array to a signed integer
    """
    unsigned=(bytearr[2]<<16)+(bytearr[3]<<8)+bytearr[4]
    return unsigned-16777216 if bytearr[2]&128 else unsigned


def bytesToUnsigned(bytearr):
    return (bytearr[1]<<24)+(bytearr[2]<<16)+(bytearr[3]<<8)+bytearr[4]

addr="addr"
mode="mode"
readconv="readconv"

_regset={
    "GCONF":      {addr: 0x00, mode:"RW"},
    "GSTAT":      {addr: 0x01, mode:"RC"},
    "IFCNT":      {addr: 0x02, mode:""},
    "SLAVECONF":  {addr: 0x03, mode:""},
    "INP_OUT":    {addr: 0x04, mode:"R"},
    "X_COMPARE":  {addr: 0x05, mode:"W"},

    "SHORT_CONF": {addr: 0x09, mode:"W"},
    "DRV_CONF":   {addr: 0x0A, mode:"W"},
    "GLBSCALER":  {addr: 0x0B, mode:"W"},

    "IHOLD_IRUN": {addr: 0x10, mode:"W"},
    "TPOWERDOWN": {addr: 0x11, mode:"W"},
    "TSTEP":      {addr: 0x12, mode:"R"},
    "TPWMTHRS":   {addr: 0x13, mode:"W"},
    "TCOOLTHRS":  {addr: 0x14, mode:"W"},
    "THIGH":      {addr: 0x15, mode:"W"},

    "RAMPMODE":   {addr: 0x20, mode:"RW"},
    "XACTUAL":    {addr: 0x21, mode:"RW"},
    "VACTUAL":    {addr: 0x22, mode:"R", readconv:bytesToSigned24},
    "VSTART":     {addr: 0x23, mode:"W"},
    "A1":         {addr: 0x24, mode:"W"},
    "V1":         {addr: 0x25, mode:"W"},
    "AMAX":       {addr: 0x26, mode:"W"},
    "VMAX":       {addr: 0x27, mode:"W"},
    "DMAX":       {addr: 0x28, mode:"W"},
    "D1":         {addr: 0x2A, mode:"W"},
    "VSTOP":      {addr: 0x2B, mode:"W"},
    "TZEROWAIT":  {addr: 0x2C, mode:"W"},
    "XTARGET":    {addr: 0x2D, mode:"RW"},

    "VDCMIN":     {addr: 0x33, mode:"W"},
    "SWMODE":     {addr: 0x34, mode:"RW"},
    "RAMPSTAT":   {addr: 0x35, mode:"RC"},
    "XLATCH":     {addr: 0x36, mode:"R"},

    "ENCMODE":    {addr: 0x38, mode:"RW"},
    "XENC":       {addr: 0x39, mode:"RW"},
    "ENC_CONST":  {addr: 0x3A, mode:"W"},
    "ENC_STATUS": {addr: 0x3B, mode:"RC"},
    "ENC_LATCH":  {addr: 0x3C, mode:"R"},

    "MSLUT0":     {addr: 0x60, mode:"W"},
    "MSLUT1":     {addr: 0x61, mode:"W"},
    "MSLUT2":     {addr: 0x62, mode:"W"},
    "MSLUT3":     {addr: 0x63, mode:"W"},
    "MSLUT4":     {addr: 0x64, mode:"W"},
    "MSLUT5":     {addr: 0x65, mode:"W"},
    "MSLUT6":     {addr: 0x66, mode:"W"},
    "MSLUT7":     {addr: 0x67, mode:"W"},
    "MSLUTSEL":   {addr: 0x68, mode:"W"},
    "MSLUTSTART": {addr: 0x69, mode:"W"},
    "MSCNT":      {addr: 0x6A, mode:"R"},
    "MSCURACT":   {addr: 0x6B, mode:"R"},

    "CHOPCONF":   {addr: 0x6C, mode:"RW"},
    "COOLCONF":   {addr: 0x6D, mode:"W"},
    "DCCTRL":     {addr: 0x6E, mode:"W"},
    "DRVSTATUS":  {addr: 0x6F, mode:"R"},
    "PWMCONF":    {addr: 0x70, mode:"W"},
    "PWMSCALE":   {addr: 0x71, mode:"R"},
    "PWM_AUTO":   {addr: 0x72, mode:"R"},
    "LOST_STEPS": {addr: 0x73, mode:"R"},
}

reglookup={
    v[addr]:k for k,v in _regset.items()
}

_statusBitLookup={
    1: 'reset'
   ,2: 'driver error'
   ,4: 'stallguard'
   ,8: 'stationary'
  ,16: 'at VMAX'
  ,32: 'at position'
  ,64: 'leftstop'
 ,128: 'rightstop'} 

_rampStatusBitLookup={
     0x01: 'limit left'
    ,0x02: 'limit right'
    ,0x04: 'latch left'
    ,0x08: 'latch right'
    ,0x10: 'stop left'
    ,0x20: 'stop right'
    ,0x40: 'event stop sg'
    ,0x80: 'pos reached event'
  ,0x0100: 'vmax reached'
  ,0x0200: 'pos reached'
  ,0x0400: 'speed zero'
  ,0x0800: 'zero transit wait'
  ,0x1000: 'reversed dir'
  ,0x2000: 'stall guard 2 active'
}

tmc5160={
    'regNames'    : _regset
   ,'statusBits'  : _statusBitLookup
   ,'statusNames' : {v: k for k,v in _statusBitLookup.items()}
   ,'rampstatBits': _rampStatusBitLookup
}
