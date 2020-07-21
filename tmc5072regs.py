#!/usr/bin/python3
"""
This defines the registers accessible via SPI for a tmc5072 with Motor 1 and 2
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
    
    "PWMCONF":    {addr: 0x10, mode:"W"},
    "PWM_STATUS": {addr: 0x11, mode:"R"},
     
    "PWMCONF2":    {addr: 0x18, mode:"W"},
    "PWM_STATUS2": {addr: 0x19, mode:"R"},

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

    "RAMPMODE2":   {addr: 0x40, mode:"RW"},
    "X2ACTUAL":    {addr: 0x41, mode:"RW"},
    "V2ACTUAL":    {addr: 0x42, mode:"R", readconv:bytesToSigned24},
    "V2START":     {addr: 0x43, mode:"W"},
    "A21":         {addr: 0x44, mode:"W"},
    "V21":         {addr: 0x45, mode:"W"},
    "A2MAX":       {addr: 0x46, mode:"W"},
    "V2MAX":       {addr: 0x47, mode:"W"},
    "D2MAX":       {addr: 0x48, mode:"W"},
    "D21":         {addr: 0x4A, mode:"W"},
    "V2STOP":      {addr: 0x4B, mode:"W"},
    "T2ZEROWAIT":  {addr: 0x4C, mode:"W"},
    "X2TARGET":    {addr: 0x4D, mode:"RW"},
    
    "IHOLD_IRUN": {addr: 0x30, mode:"W"},
    "TCOOLTHRS":  {addr: 0x31, mode:"W"},
    "THIGH":      {addr: 0x32, mode:"W"},
    "VDCMIN":     {addr: 0x33, mode:"W"},
    "SWMODE":     {addr: 0x34, mode:"RW"},
    "RAMPSTAT":   {addr: 0x35, mode:"RC"},
    "XLATCH":     {addr: 0x36, mode:"R"},

    "IHOLD_IRUN2": {addr: 0x50, mode:"W"},
    "T2COOLTHRS":  {addr: 0x51, mode:"W"},
    "T2HIGH":      {addr: 0x52, mode:"W"},
    "VDCMIN2":     {addr: 0x53, mode:"W"},
    "SWMODE2":     {addr: 0x54, mode:"RW"},
    "RAMPSTAT2":   {addr: 0x55, mode:"RC"},
    "X2LATCH":     {addr: 0x56, mode:"R"},

    "ENCMODE":    {addr: 0x38, mode:"RW"},
    "XENC":       {addr: 0x39, mode:"RW"},
    "ENC_CONST":  {addr: 0x3A, mode:"W"},
    "ENC_STATUS": {addr: 0x3B, mode:"RC"},
    "ENC_LATCH":  {addr: 0x3C, mode:"R"},

    "ENCMODE2":    {addr: 0x58, mode:"RW"},
    "XENC2":       {addr: 0x59, mode:"RW"},
    "ENC_CONST2":  {addr: 0x5A, mode:"W"},
    "ENC_STATUS2": {addr: 0x5B, mode:"RC"},
    "ENC_LATCH2":  {addr: 0x5C, mode:"R"},

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
   

    "MSCNT2":      {addr: 0x7A, mode:"R"},
    "MSCURACT2":   {addr: 0x7B, mode:"R"},
    "CHOPCONF2":   {addr: 0x7C, mode:"RW"},
    "COOLCONF2":   {addr: 0x7D, mode:"W"},
    "DCCTRL2":     {addr: 0x7E, mode:"W"},
    "DRVSTATUS2":  {addr: 0x7F, mode:"R"},
    
}

reglookup={
    v[addr]:k for k,v in _regset.items()
}

_statusBitLookup={
    1: 'reset'
   ,2: 'driver 1 error'
   ,4: 'driver 2 error'
   ,8: 'stallguard'
  ,16: 'stationary'
  ,32: 'at VMAX'
  ,64: 'at position'
 ,128: 'leftstop'
 ,256: 'rightstop'} 

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

tmc5072={
    'regNames'    : _regset
   ,'statusBits'  : _statusBitLookup
   ,'statusNames' : {v: k for k,v in _statusBitLookup.items()}
   ,'rampstatBits': _rampStatusBitLookup
}
