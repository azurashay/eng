"""Regenerate arabic/audio.js (built-in Arabic pronunciation clips).

Steps:
  1. node arabic/tools/list_texts.js            -> writes texts.json (every text the app speaks)
  2. pip install sherpa-onnx==1.12.40            (2.x dropped the espeak frontend this voice needs)
  3. download + extract https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-ar_JO-kareem-medium.tar.bz2
  4. python3 arabic/tools/make_audio.py texts.json <model-dir> arabic/audio.js   (needs ffmpeg)

prep() rewrites the vocalised text so espeak/Piper pronounces it the way it is taught.
"""
import json, os, re, sys, wave, base64, subprocess, tempfile
import re
SUN='تثدذرزسشصضطظلن'
OVR={'جَيِّد':'جَيْيِد','اَلِاثْنَيْن':'اَلْإِثْنَيْن','مَا اسْمُكَ؟':'مَسْمُكَ؟'}
DIG={'٠':'صِفْر','١':'وَاحِد','٢':'اِثْنَان','٣':'ثَلَاثَة','٤':'أَرْبَعَة','٥':'خَمْسَة','٦':'سِتَّة','٧':'سَبْعَة','٨':'ثَمَانِيَة','٩':'تِسْعَة','١٠':'عَشَرَة'}
def prep(t):
    t=OVR.get(t,t); t=DIG.get(t,t)
    t=t.replace('\u0640','')
    t=re.sub(r'([\u064B-\u0650])\u0651','\u0651\\1',t)
    t=re.sub(r'^اَ?ل\u0652?(?=['+SUN+']\u0651)','اَ',t)
    t=re.sub(r'(?<=\s)ا[\u064E\u0650]?ل\u0652?(?=['+SUN+']\u0651)','',t)
    t=re.sub(r'(?<=\s)ا[\u064E\u0650]?(?=ل)','',t)
    t=re.sub(r'ة[\u064E\u064F\u0650]?(?=$|[\s؟،!.])','',t)
    # unvowelled word-final consonant gets a sukun (otherwise espeak may add a vowel)
    t=re.sub(r'([بتثجحخدذرزسشصضطظعغفقكلمنه])(?=$|[\s؟،!.])','\\1\u0652',t)
    # a lone consonant+short vowel can be read as the vowel's name; a leading tatweel avoids it
    # espeak reads a word-initial ب ف ك ل س as a prefix and leaves the word unstressed; a tatweel prevents it
    t=re.sub(r'(?:^|(?<=\s))(?=[بفكلس])','\u0640',t)
    if re.fullmatch(r'[\u0621-\u064A][\u064E\u064F\u0650]',t): t=t if t.startswith('\u0640') else '\u0640'+t
    return t

def main(texts_path, model_dir, out_js):
    import numpy as np, sherpa_onnx
    M = model_dir.rstrip('/') + '/'
    tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=M + 'ar_JO-kareem-medium.onnx', tokens=M + 'tokens.txt',
                                                   data_dir=M + 'espeak-ng-data'), num_threads=4)))
    texts = json.load(open(texts_path, encoding='utf-8'))
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        wav, mp3 = os.path.join(tmp, 'w.wav'), os.path.join(tmp, 'w.mp3')
        for t in texts:
            p = prep(t)
            short = len(re.sub(r'[ً-ْـ]', '', p)) <= 4
            # the voice cuts very short utterances off; framing with commas lets them finish
            a = tts.generate('، ' + p + ' ،', sid=0, speed=0.7 if short else 0.85)
            pcm = (np.clip(np.array(a.samples), -1, 1) * 32767).astype('<i2')
            with wave.open(wav, 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(a.sample_rate); w.writeframes(pcm.tobytes())
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-af',
                            'silenceremove=start_periods=1:start_threshold=-50dB,areverse,'
                            'silenceremove=start_periods=1:start_threshold=-50dB,areverse,'
                            'apad=pad_dur=0.15,loudnorm=I=-16:TP=-1.5',
                            '-ac', '1', '-ar', '22050', '-b:a', '48k', mp3], check=True)
            out[t] = base64.b64encode(open(mp3, 'rb').read()).decode()
    with open(out_js, 'w', encoding='utf-8') as f:
        f.write('// Arabic pronunciation clips (MP3, base64), generated offline with the Piper ar_JO "kareem" voice.\n'
                '// Keyed by the exact Arabic text the app speaks (item.say / letter example word).\n'
                '// Regenerate with arabic/tools/make_audio.py.\n')
        f.write('window.AUDIO_DATA=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(len(out), 'clips ->', out_js)

if __name__ == '__main__':
    main(*sys.argv[1:4])
