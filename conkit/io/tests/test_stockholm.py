"""Testing facility for conkit.io.StockholmIO"""

__author__ = "Felix Simkovic"
__date__ = "12 Sep 2016"

import os
import unittest

from conkit.io.stockholm import StockholmParser
from conkit.io.tests.helpers import ParserTestCase


class TestStockholmParser(ParserTestCase):
    def test_read_1(self):
        msa = """# STOCKHOLM 1.0
#=GF ID 1EAZ:A|PDBID|CHAIN|SEQUENCE-i5

#=GS UniRef100_A0A0D2WIY8/647-745      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3
#=GS UniRef100_A0A0D2WIY8/761-857      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3
#=GS UniRef100_A0A0D2WIY8/1126-1228    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3
#=GS UniRef100_A0A0D2WIY8/1245-1341    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3
#=GS UniRef100_A0A0D2WIY8/1752-1857    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3

1EAZ:A|PDBID|CHAIN|SEQUENCE               GSMFTPKPPQDSAVIKAG-YC-V------K-Q-------------------------------------------------G-A------------VM------------------------------------------------------------------------------------------------------
UniRef100_A0A0D2WIY8/647-745              ---------------IEG-YL-S------K-Q-------------------------------------------------G-GV----------NNN------------------------------------------------------------------------------------------------------
#=GR UniRef100_A0A0D2WIY8/647-745      PP ...............79*.**.*......*.*.................................................*.99..........9**......................................................................................................
UniRef100_A0A0D2WIY8/761-857              -----------ANPDKEG-WL-K------K-Q-------------------------------------------------G-N-----------SMA------------------------------------------------------------------------------------------------------
#=GR UniRef100_A0A0D2WIY8/761-857      PP ...........5899***.**.*......*.*.................................................*.9...........9**......................................................................................................
UniRef100_A0A0D2WIY8/1126-1228            ------------AVRKLG-FL-Y------K-Q-------------------------------------------------G-G------------SN------------------------------------------------------------------------------------------------------
#=GR UniRef100_A0A0D2WIY8/1126-1228    PP ............68999*.**.*......*.*.................................................*.*............**......................................................................................................
UniRef100_A0A0D2WIY8/1245-1341            ------------NPARQG-WL-C------K-R-------------------------------------------------G-G------------TY------------------------------------------------------------------------------------------------------
#=GR UniRef100_A0A0D2WIY8/1245-1341    PP ............6789**.**.*......*.*.................................................*.*............**......................................................................................................
UniRef100_A0A0D2WIY8/1752-1857            -------QRATPGFKMKG-WL-H------K-E-------------------------------------------------G-G------------SV------------------------------------------------------------------------------------------------------
#=GR UniRef100_A0A0D2WIY8/1752-1857    PP .......556677889**.**.*......*.*.................................................*.*............**......................................................................................................
#=GC PP_cons                              .......*....*...................................*.....*..*................*.................*..*....*................................................*****999875555677766776.
#=GC RF                                   .......x....x...................................x.....x..x................x.................x..x....x................................................xxxxxxxxxxxxxxxxxxxxxxxx

1EAZ:A|PDBID|CHAIN|SEQUENCE               -------------------K-----------------------NW---------------------------------------------------------------------------------------------K--R-R------------Y----F-QL--------D--E-----------------------
UniRef100_A0A0D2WIY8/647-745              -------------------K-----------------------GW---------------------------------------------------------------------------------------------K--R-R------------Y----C-VL--------E--N-----------------------
#=GR UniRef100_A0A0D2WIY8/647-745      PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................
UniRef100_A0A0D2WIY8/761-857              -------------------K-----------------------DW---------------------------------------------------------------------------------------------K--K-R------------Y----I-AI--------K--E-----------------------
#=GR UniRef100_A0A0D2WIY8/761-857      PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................
UniRef100_A0A0D2WIY8/1126-1228            -------------------K-----------------------GW---------------------------------------------------------------------------------------------R--K-R------------W----I-VM--------E--H-----------------------
#=GR UniRef100_A0A0D2WIY8/1126-1228    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................
UniRef100_A0A0D2WIY8/1245-1341            -------------------T-----------------------SW---------------------------------------------------------------------------------------------K--K-R------------W----L-VL--------K--G-----------------------
#=GR UniRef100_A0A0D2WIY8/1245-1341    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................
UniRef100_A0A0D2WIY8/1752-1857            -------------------K-----------------------TW---------------------------------------------------------------------------------------------K--R-R------------W----F-ST--------T--P-----------------------
#=GR UniRef100_A0A0D2WIY8/1752-1857    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................
#=GC PP_cons                              ...................9.......................**.............................................................................................*..*.*............*....*.**........9..9.......................
#=GC RF                                   ...................x.......................xx.............................................................................................x..x.x............x....x.xx........x..x.......................
//
"""
        f_name = self.tempfile(content=msa)
        parser = StockholmParser()
        with open(f_name, "r") as f_in:
            hierarchy = parser.read(f_in)
        for i, sequence_entry in enumerate(hierarchy):
            if i == 0:
                self.assertEqual("1EAZ:A|PDBID|CHAIN|SEQUENCE", sequence_entry.id)
                self.assertEqual(
                    "GSMFTPKPPQDSAVIKAG-YC-V------K-Q-------------------------------------------------G-A-"
                    "-----------VM------------------------------------------------------------------------"
                    "-------------------------------------------------K-----------------------NW----------"
                    "-----------------------------------------------------------------------------------K-"
                    "-R-R------------Y----F-QL--------D--E-----------------------",
                    sequence_entry.seq,
                )
            elif i == 1:
                self.assertEqual("UniRef100_A0A0D2WIY8/647-745", sequence_entry.id)
                self.assertEqual(
                    "---------------IEG-YL-S------K-Q-------------------------------------------------G-GV"
                    "----------NNN------------------------------------------------------------------------"
                    "-------------------------------------------------K-----------------------GW----------"
                    "-----------------------------------------------------------------------------------K-"
                    "-R-R------------Y----C-VL--------E--N-----------------------",
                    sequence_entry.seq,
                )
                self.assertEqual(
                    [
                        "[subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=C"
                        "apsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3"
                    ],
                    sequence_entry.remark,
                )
            elif i == 2:
                self.assertEqual("UniRef100_A0A0D2WIY8/761-857", sequence_entry.id)
                self.assertEqual(
                    "-----------ANPDKEG-WL-K------K-Q-------------------------------------------------G-N-"
                    "----------SMA------------------------------------------------------------------------"
                    "-------------------------------------------------K-----------------------DW----------"
                    "-----------------------------------------------------------------------------------K-"
                    "-K-R------------Y----I-AI--------K--E-----------------------",
                    sequence_entry.seq,
                )
                self.assertEqual(
                    [
                        "[subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=C"
                        "apsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3"
                    ],
                    sequence_entry.remark,
                )
            elif i == 3:
                self.assertEqual("UniRef100_A0A0D2WIY8/1126-1228", sequence_entry.id)
                self.assertEqual(
                    "------------AVRKLG-FL-Y------K-Q-------------------------------------------------G-G-"
                    "-----------SN------------------------------------------------------------------------"
                    "-------------------------------------------------K-----------------------GW----------"
                    "-----------------------------------------------------------------------------------R-"
                    "-K-R------------W----I-VM--------E--H-----------------------",
                    sequence_entry.seq,
                )
                self.assertEqual(
                    [
                        "[subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=C"
                        "apsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3"
                    ],
                    sequence_entry.remark,
                )
            elif i == 4:
                self.assertEqual("UniRef100_A0A0D2WIY8/1245-1341", sequence_entry.id)
                self.assertEqual(
                    "------------NPARQG-WL-C------K-R-------------------------------------------------G-G-"
                    "-----------TY------------------------------------------------------------------------"
                    "-------------------------------------------------T-----------------------SW----------"
                    "-----------------------------------------------------------------------------------K-"
                    "-K-R------------W----L-VL--------K--G-----------------------",
                    sequence_entry.seq,
                )
                self.assertEqual(
                    [
                        "[subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=C"
                        "apsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3"
                    ],
                    sequence_entry.remark,
                )
            elif i == 5:
                self.assertEqual("UniRef100_A0A0D2WIY8/1752-1857", sequence_entry.id)
                self.assertEqual(
                    "-------QRATPGFKMKG-WL-H------K-E-------------------------------------------------G-G-"
                    "-----------SV------------------------------------------------------------------------"
                    "-------------------------------------------------K-----------------------TW----------"
                    "-----------------------------------------------------------------------------------K-"
                    "-R-R------------W----F-ST--------T--P-----------------------",
                    sequence_entry.seq,
                )
                self.assertEqual(
                    [
                        "[subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=C"
                        "apsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3"
                    ],
                    sequence_entry.remark,
                )

    def test_write_1(self):
        msa = [
            "# STOCKHOLM 1.0",
            "#=GF ID 1EAZ:A|PDBID|CHAIN|SEQUENCE-i5",
            "",
            "#=GS UniRef100_A0A0D2WIY8/647-745      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/761-857      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1126-1228    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1245-1341    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1752-1857    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "",
            "1EAZ:A|PDBID|CHAIN|SEQUENCE               GSMFTPKPPQDSAVIKAG-YC-V------K-Q-------------------------------------------------G-A------------VM------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/647-745              ---------------IEG-YL-S------K-Q-------------------------------------------------G-GV----------NNN------------------------------------------------------------------------------------------------------",
            "#=GR UniRef100_A0A0D2WIY8/647-745      PP ...............79*.**.*......*.*.................................................*.99..........9**......................................................................................................",
            "UniRef100_A0A0D2WIY8/761-857              -----------ANPDKEG-WL-K------K-Q-------------------------------------------------G-N-----------SMA------------------------------------------------------------------------------------------------------",
            "#=GR UniRef100_A0A0D2WIY8/761-857      PP ...........5899***.**.*......*.*.................................................*.9...........9**......................................................................................................",
            "UniRef100_A0A0D2WIY8/1126-1228            ------------AVRKLG-FL-Y------K-Q-------------------------------------------------G-G------------SN------------------------------------------------------------------------------------------------------",
            "#=GR UniRef100_A0A0D2WIY8/1126-1228    PP ............68999*.**.*......*.*.................................................*.*............**......................................................................................................",
            "UniRef100_A0A0D2WIY8/1245-1341            ------------NPARQG-WL-C------K-R-------------------------------------------------G-G------------TY------------------------------------------------------------------------------------------------------",
            "#=GR UniRef100_A0A0D2WIY8/1245-1341    PP ............6789**.**.*......*.*.................................................*.*............**......................................................................................................",
            "UniRef100_A0A0D2WIY8/1752-1857            -------QRATPGFKMKG-WL-H------K-E-------------------------------------------------G-G------------SV------------------------------------------------------------------------------------------------------",
            "#=GR UniRef100_A0A0D2WIY8/1752-1857    PP .......556677889**.**.*......*.*.................................................*.*............**......................................................................................................",
            "#=GC PP_cons                              .......*....*...................................*.....*..*................*.................*..*....*................................................*****999875555677766776.",
            "#=GC RF                                   .......x....x...................................x.....x..x................x.................x..x....x................................................xxxxxxxxxxxxxxxxxxxxxxxx",
            "",
            "1EAZ:A|PDBID|CHAIN|SEQUENCE               -------------------K-----------------------NW---------------------------------------------------------------------------------------------K--R-R------------Y----F-QL--------D--E-----------------------",
            "UniRef100_A0A0D2WIY8/647-745              -------------------K-----------------------GW---------------------------------------------------------------------------------------------K--R-R------------Y----C-VL--------E--N-----------------------",
            "#=GR UniRef100_A0A0D2WIY8/647-745      PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................",
            "UniRef100_A0A0D2WIY8/761-857              -------------------K-----------------------DW---------------------------------------------------------------------------------------------K--K-R------------Y----I-AI--------K--E-----------------------",
            "#=GR UniRef100_A0A0D2WIY8/761-857      PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................",
            "UniRef100_A0A0D2WIY8/1126-1228            -------------------K-----------------------GW---------------------------------------------------------------------------------------------R--K-R------------W----I-VM--------E--H-----------------------",
            "#=GR UniRef100_A0A0D2WIY8/1126-1228    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................",
            "UniRef100_A0A0D2WIY8/1245-1341            -------------------T-----------------------SW---------------------------------------------------------------------------------------------K--K-R------------W----L-VL--------K--G-----------------------",
            "#=GR UniRef100_A0A0D2WIY8/1245-1341    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................",
            "UniRef100_A0A0D2WIY8/1752-1857            -------------------K-----------------------TW---------------------------------------------------------------------------------------------K--R-R------------W----F-ST--------T--P-----------------------",
            "#=GR UniRef100_A0A0D2WIY8/1752-1857    PP ...................*.......................**.............................................................................................*..*.*............*....*.**........*..*.......................",
            "#=GC PP_cons                              ...................9.......................**.............................................................................................*..*.*............*....*.**........9..9.......................",
            "#=GC RF                                   ...................x.......................xx.............................................................................................x..x.x............x....x.xx........x..x.......................",
            "//",
        ]
        parser = StockholmParser()
        f_name_in = self.tempfile(content="\n".join(msa))
        f_name_out = self.tempfile()
        with open(f_name_in, "r") as f_in, open(f_name_out, "w") as f_out:
            hierarchy = parser.read(f_in)
            parser.write(f_out, hierarchy)

        ref = [
            "# STOCKHOLM 1.0",
            "#=GF ID 1EAZ:A|PDBID|CHAIN|SEQUENCE",
            "",
            "#=GS UniRef100_A0A0D2WIY8/647-745      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/761-857      DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1126-1228    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1245-1341    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "#=GS UniRef100_A0A0D2WIY8/1752-1857    DE [subseq from] Stromal membrane-associated GTPase-activating protein 2 n=1 Tax=Capsaspora owczarzaki (strain ATCC 30864) RepID=A0A0D2WIY8_CAPO3",
            "",
            "1EAZ:A|PDBID|CHAIN|SEQUENCE               GSMFTPKPPQDSAVIKAG-YC-V------K-Q-------------------------------------------------G-A------------VM------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/647-745              ---------------IEG-YL-S------K-Q-------------------------------------------------G-GV----------NNN------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/761-857              -----------ANPDKEG-WL-K------K-Q-------------------------------------------------G-N-----------SMA------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/1126-1228            ------------AVRKLG-FL-Y------K-Q-------------------------------------------------G-G------------SN------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/1245-1341            ------------NPARQG-WL-C------K-R-------------------------------------------------G-G------------TY------------------------------------------------------------------------------------------------------",
            "UniRef100_A0A0D2WIY8/1752-1857            -------QRATPGFKMKG-WL-H------K-E-------------------------------------------------G-G------------SV------------------------------------------------------------------------------------------------------",
            "",
            "1EAZ:A|PDBID|CHAIN|SEQUENCE               -------------------K-----------------------NW---------------------------------------------------------------------------------------------K--R-R------------Y----F-QL--------D--E-----------------------",
            "UniRef100_A0A0D2WIY8/647-745              -------------------K-----------------------GW---------------------------------------------------------------------------------------------K--R-R------------Y----C-VL--------E--N-----------------------",
            "UniRef100_A0A0D2WIY8/761-857              -------------------K-----------------------DW---------------------------------------------------------------------------------------------K--K-R------------Y----I-AI--------K--E-----------------------",
            "UniRef100_A0A0D2WIY8/1126-1228            -------------------K-----------------------GW---------------------------------------------------------------------------------------------R--K-R------------W----I-VM--------E--H-----------------------",
            "UniRef100_A0A0D2WIY8/1245-1341            -------------------T-----------------------SW---------------------------------------------------------------------------------------------K--K-R------------W----L-VL--------K--G-----------------------",
            "UniRef100_A0A0D2WIY8/1752-1857            -------------------K-----------------------TW---------------------------------------------------------------------------------------------K--R-R------------W----F-ST--------T--P-----------------------",
            "//",
        ]
        with open(f_name_out, "r") as f_in:
            output = f_in.read().splitlines()
        self.assertEqual(ref, output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
