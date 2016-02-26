#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import argparse
import ast
import binascii
import hashlib
import random
import readline
import sys
import traceback
from types import *
import SeriouslyCommands

anytype = SeriouslyCommands.anytype

cp437table = ''.join(map(chr,list(range(128)))) + "ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ "

def ord_cp437(c):
    return cp437table.index(c)
    
def chr_cp437(o):
    return cp437table[o]

class Seriously(object):
    @classmethod
    def _make_new(cls,init_stack=[], debug_mode=False, repl_mode=False):
        return cls(init_stack, debug_mode, repl_mode)
    def make_new(self,*stack):
        return self._make_new(init_stack=list(stack), debug_mode=self.debug_mode)
        return res
    def __init__(self, init_stack=[], debug_mode=False, repl_mode=False, hex_mode=False):
        self.stack = init_stack
        self.debug_mode=debug_mode
        self.repl_mode = repl_mode
        self.fn_table = SeriouslyCommands.fn_table
        self.code = ''
        self.hex_mode = hex_mode
        self.preserve = False
        self.pop_counter = 0
    def push(self,val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop() if not self.preserve else self.preserve_pop()
    def preserve_pop(self):
        v = self.stack.pop()
        self.push(v)
        return v
    def peek(self):
        return self.stack[-1] if self.stack else None
    def prepend(self, val):
        self.stack[:] = [val] + self.stack
    def toggle_preserve(self):
        self.preserve = not self.preserve
    def eval(self, code, print_at_end=True):
        if self.hex_mode:
            code = binascii.unhexlify(code).decode('cp437')
        if self.debug_mode:
            print(code)
        i=0
        if self.repl_mode:
            self.code += code
        else:
            self.code = code
        while i < len(code):
            old_stack = self.stack[:]
            try:
                c = code[i]
                if c == '"':
                    s = ""
                    i+=1
                    while i<len(code) and code[i]!='"':
                        s+=code[i]
                        i+=1
                    self.push(s)
                if ord_cp437(c) == 0xEC:
                    s = ""
                    i+=1
                    while i<len(code) and ord_cp437(code[i]) != 0xEC:
                        s+=code[i]
                        i+=1
                    r = eval(s)
                    if r is not None:
                        self.push(r)
                elif c == "'":
                    i+=1
                    self.push(code[i])
                elif c == ':':
                    v = ""
                    i+=1
                    while i<len(code) and code[i]!=':':
                        v+=code[i]
                        i+=1
                    val = 0
                    try:
                        val = eval(v)
                    except:
                        pass
                    val = val if anytype(val, int, float, complex) else 0
                    self.push(val)
                elif c == 'W':
                    inner = ''
                    i+=1
                    while i<len(code) and code[i]!='W':
                        inner+=code[i]
                        i+=1
                    if self.debug_mode:
                        print("while loop code: %s"%inner)
                    while self.peek():
                        self.eval(inner, print_at_end=False)
                elif c == '[':
                    l = ''
                    i+=1
                    while i<len(code) and code[i]!=']':
                        l+=code[i]
                        i+=1
                    self.push(eval('[%s]'%l))
                elif c == '`':
                    f = ''
                    i+=1
                    while i<len(code) and code[i]!='`':
                        f+=code[i]
                        i+=1
                    self.push(SeriouslyCommands.SeriousFunction(f))
                elif ord(c) in range(48,58):
                    self.push(int(c))
                else:
                    if self.debug_mode:
                        print(binascii.hexlify(chr(ord_cp437(c)).encode()).decode().upper())
                    self.fn_table.get(ord_cp437(c), lambda x:x)(self)
                    if self.debug_mode:
                        print(self.stack)
            except SystemExit:
                exit()
            except KeyboardInterrupt:
                exit()
            except:
                if self.debug_mode:
                    traceback.print_exc()
                self.stack = old_stack[:]
            finally:
                i+=1
        if not self.repl_mode and print_at_end:
            while len(self.stack) > 0:
                print(self.pop())

def srs_repl(debug_mode=False, quiet_mode=False, hex=False):
    srs = Seriously(repl_mode=True, debug_mode=debug_mode, hex_mode=hex)
    while 1:
        try:
            srs.eval(input('' if quiet_mode else '>>> '))
        except EOFError:
            exit()
        finally:
            if not quiet_mode:
                print('\n')
                print(srs.stack)
            
def srs_exec(debug_mode=False, file_obj=None, code=None, hex=False):
    srs = Seriously(debug_mode=debug_mode, hex_mode=hex)
    if file_obj:
        srs.eval(file_obj.read())
        file_obj.close()
    else:
        srs.eval(code)
                
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Seriously interpreter")
    parser.add_argument("-d", "--debug", help="turn on debug mode", action="store_true")
    parser.add_argument("-q", "--quiet", help="turn off REPL prompts and automatic stack printing, only print code STDOUT output", action="store_true")
    parser.add_argument("-x", "--hex", help="turn on hex mode (code is taken in hex values instead of binary bytes)", action="store_true")
    parser.add_argument("-i", "--ide", help="turn on IDE mode, which disables unsafe commands", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--code", help="run the specified code")
    group.add_argument("-f", "--file", help="specify an input file", type=argparse.FileType('r'))
    args = parser.parse_args()
    if args.ide:
        commands.fn_table[0xF0] = lambda x: x.push(ast.literal_eval(x.pop()))
    if args.code or args.file:
        srs_exec(args.debug, args.file, args.code, args.hex)
    else:
        srs_repl(args.debug, args.quiet, args.hex)