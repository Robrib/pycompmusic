# -*- coding: utf-8 -*-
# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/
#
# If you are using this extractor please cite the following paper:
#
# Atlı, H. S., Uyar, B., Şentürk, S., Bozkurt, B., and Serra, X. (2014). Audio
# feature extraction for exploring Turkish makam music. In Proceedings of 3rd
# International Conference on Audio Technologies for Music and Media, Ankara,
# Turkey.
import os
import re
import json
import tempfile

import compmusic.extractors
from docserver import util
from musicxmlconverter.symbtr2musicxml import symbtrscore
from subprocess import call
from os.path import isfile, join
from musicxml2lilypond import ScoreConverter
from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class Symbtr2Png(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrtxt"
    _slug = "score"
    _output = {
            "intervals": {"extension": "json", "mimetype": "application/json"},
            "xmlscore": {"extension": "xml", "mimetype": "application/xml"},
            "score": {"extension": "svg", "mimetype": "image/svg+xml", "parts": True},
            "indexmap": {"extension": "json", "mimetype": "application/json"},
    }


    def run(self, musicbrainzid, fpath):
        symbtrmu2 = util.docserver_get_symbtrmu2(musicbrainzid)
        print symbtrmu2
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        fname = symbtr['name']
        finfo = fname.split('/')[-1]

        fp, tmpxml = tempfile.mkstemp(".xml")
        os.close(fp)

        mbid_url = 'http://musicbrainz.org/work/%s' % musicbrainzid

        piece = symbtrscore(fpath, symbtrmu2, symbtrname=finfo, mbid_url=mbid_url)
        piece.convertsymbtr2xml() 
        piece.writexml(tmpxml)
        intervals = piece.get_measure_bounds()

        conv = ScoreConverter(tmpxml)
        conv.run()


        tmp_dir = tempfile.mkdtemp()
        call(["lilypond", '-dpaper-size=\"junior-legal\"', "-dbackend=svg", "-o" "%s" % (tmp_dir), tmpxml.replace(".xml",".ly")])

        ret = {'intervals': intervals, 'score': [], 'xmlscore': '', 'indexmap': ''}
        musicxml = open(tmpxml)
        ret['xmlscore'] = musicxml.read()
        musicxml.close()
        indexmap = open(tmpxml.replace('.xml','.json'))
        ret['indexmap'] = json.loads(indexmap.read())
        indexmap.close()

        os.unlink(tmpxml)
        os.unlink(tmpxml.replace('.xml','.ly'))
        os.unlink(tmpxml.replace('.xml','.json'))

        regex = re.compile(r'.*<a style="(.*)" xlink:href="textedit:\/\/\/.*:([0-9]+):([0-9]+):([0-9]+)">.*')
        files = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)]
        files = filter(os.path.isfile, files)
        files.sort(key=lambda x: os.path.getmtime(x))

        for f in files:
            if f.endswith('.svg'):
                svg_file = open(f)
                score = svg_file.read()
                ret['score'].append(regex.sub(r'<a style="\1" id="l\2-f\3-t\4" from="\3" to="\4">',score))
                svg_file.close()
                os.remove(f)
        os.rmdir(tmp_dir)
        return ret



