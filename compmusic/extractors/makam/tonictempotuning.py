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
import os
import compmusic.extractors
import subprocess
import socket
import json

import tempfile
import wave
import subprocess
from docserver import util

from ahenkidentifier import ahenkidentifier
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class TonicTempoTuning(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "tonictempotuning"
    _depends = "metadata"

    _output = {
         "tonic": {"extension": "json", "mimetype": "application/json"},
         "tempo": {"extension": "json", "mimetype": "application/json"},
         "tuning": {"extension": "json", "mimetype": "application/json"},
          "ahenk": {"extension": "json", "mimetype": "application/json"}
         }

    def run(self, musicbrainzid, fname):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["MCR_CACHE_ROOT"] = "/tmp/emptydir"
        subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        #subprocess_env["LD_LIBRARY_PATH"] = "/usr/local/MATLAB/MATLAB_Runtime/v85/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/os/glnxa64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/server"
        rec_data = dunya.makam.get_recording(musicbrainzid)
        
        if len(rec_data['works']) == 0:
            raise Exception('No work on recording %s' % musicbrainzid)

        ret = {'tempo':{}, 'tonic':{}, 'tuning':{}, "ahenk": {}}
        for w in rec_data['works']:

            symbtrtxt =util.docserver_get_symbtrtxt(w['mbid'])
            if not symbtrtxt:
                continue
 
            metadata = util.docserver_get_filename(w['mbid'], "metadata", "metadata", version="0.1")

            mp3file, created = util.docserver_get_wav_filename(musicbrainzid)
            mlbinary = util.docserver_get_filename(musicbrainzid, "initialmakampitch", "matlab", version="0.6")
            output = tempfile.mkdtemp()
            print "/srv/dunya/extractTonicTempoTuning %s %s %s %s %s" % (symbtrtxt, metadata, mp3file, mlbinary, output)   
            proc = subprocess.Popen(["/srv/dunya/extractTonicTempoTuning %s %s %s %s %s" % (symbtrtxt, metadata, mp3file, mlbinary, output)], stdout=subprocess.PIPE, shell=True, env=subprocess_env)
           
            
            (out, err) = proc.communicate()
            if created:
                os.unlink(mp3file)
            expected = ['tempo', 'tonic', 'tuning'] 
            for f in expected:
                if os.path.isfile(os.path.join(output, f + '.json')):
                    json_file = open(os.path.join(output, f + '.json'))
                    ret[f][w['mbid']] = json.loads(json_file.read())
                    json_file.close()
                    os.remove(os.path.join(output, f + '.json'))
                else:
                    raise Exception('Missing output %s file for %s' % (f, musicbrainzid))
            os.rmdir(output)
            
            scorename = compmusic.dunya.makam.get_symbtr(w['mbid'])
            splitted = scorename['name'].split('/')[-1].split('--')
            makam = splitted[0]
            ahenk = ahenkidentifier.identify(ret['tonic'][w['mbid']]['scoreInformed']['Value'], makam)
            ret["ahenk"][w['mbid']] = ahenk
             
        
        return ret 
