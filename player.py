import subprocess
import time
import threading
import signal

class AudioPlayer:
    def __init__(self):
        self.process = None
        self.current_track = None
        self.current_stream_url = None
        self.start_time = 0
        self.is_paused = False
        self.pause_start = 0
        self.total_paused_duration = 0
        self._monitor_thread = None
        self.on_track_end_callback = None
        self._manual_seek_or_stop = False

    def play(self, stream_url: str, track_info: dict, start_sec: float = 0.0):
        self.stop()
        self.current_track = track_info
        self.current_stream_url = stream_url
        self.start_time = time.time() - start_sec
        self.is_paused = False
        self.total_paused_duration = 0
        self._manual_seek_or_stop = False

        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        if start_sec > 0:
            cmd.extend(["-ss", str(int(start_sec))])
        cmd.append(stream_url)

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()
            return True
        except Exception as e:
            print(f"Player error: {e}")
            return False

    def seek(self, delta_seconds: float) -> bool:
        """Seek forward or backward by delta_seconds (e.g. +10 or -10)."""
        if not self.process or not self.current_stream_url:
            return False

        current_pos = self.get_elapsed_seconds()
        target_pos = max(0.0, current_pos + delta_seconds)

        self._manual_seek_or_stop = True
        try:
            if self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=0.3)
        except Exception:
            pass

        return self.play(self.current_stream_url, self.current_track, start_sec=target_pos)

    def toggle_pause(self) -> bool:
        """Toggle pause state using SIGSTOP/SIGCONT signals."""
        if not self.process or self.process.poll() is not None:
            return False

        if not self.is_paused:
            try:
                self.process.send_signal(signal.SIGSTOP)
                self.is_paused = True
                self.pause_start = time.time()
                return True
            except Exception:
                return False
        else:
            try:
                self.process.send_signal(signal.SIGCONT)
                self.is_paused = False
                self.total_paused_duration += (time.time() - self.pause_start)
                return True
            except Exception:
                return False

    def _monitor(self):
        if self.process:
            self.process.wait()
            if not self._manual_seek_or_stop and self.on_track_end_callback:
                self.on_track_end_callback()

    def stop(self):
        self._manual_seek_or_stop = True
        if self.process:
            try:
                proc = self.process
                self.process = None
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=0.3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        self.current_track = None
        self.current_stream_url = None
        self.is_paused = False

    def get_elapsed_seconds(self) -> float:
        if not self.process or self.start_time == 0:
            return 0.0
        if self.is_paused:
            return self.pause_start - self.start_time - self.total_paused_duration
        return time.time() - self.start_time - self.total_paused_duration

    def is_playing(self) -> bool:
        return self.process is not None and self.process.poll() is None
