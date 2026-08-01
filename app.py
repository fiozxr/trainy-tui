import asyncio
import random
import time
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer, Input, DataTable, Static, Label, Button, ContentSwitcher
from textual import work, on

from api import TrainyAPI
from player import AudioPlayer

CSS = """
Screen {
    layout: vertical;
    background: #000000;
    color: #ffffff;
}

#top-nav-bar {
    height: 3;
    background: #111111;
    border-bottom: solid #333333;
    layout: horizontal;
    align: left middle;
    padding: 0 1;
}

#brand-label {
    text-style: bold;
    color: #ffffff;
    padding-left: 1;
}

#nav-buttons-container {
    layout: horizontal;
}

.nav-btn {
    background: #1a1a1a;
    color: #aaaaaa;
    border: solid #333333;
    margin: 0 1;
    min-width: 12;
}

.nav-btn:hover {
    background: #333333;
    color: #ffffff;
}

.nav-btn-active {
    background: #ffffff;
    color: #000000;
    text-style: bold;
    border: solid #ffffff;
}

#main-content-switcher {
    height: 1fr;
    background: #050505;
}

/* HOME / SEARCH VIEW */
#view-home {
    layout: vertical;
    padding: 1 2;
    height: 1fr;
}

#search-input {
    border: solid #444444;
    background: #080808;
    color: #ffffff;
    margin-bottom: 1;
}

#search-input:focus {
    border: solid #ffffff;
}

#home-split {
    layout: horizontal;
    height: 1fr;
}

#tracks-panel {
    width: 60%;
    border: solid #333333;
    background: #050505;
    padding: 0 1;
}

#lyrics-side-panel {
    width: 40%;
    border: solid #333333;
    background: #080808;
    padding: 1;
    margin-left: 1;
}

#lyrics-side-title {
    text-style: bold;
    border-bottom: solid #333333;
    margin-bottom: 1;
}

#lyrics-side-text {
    height: 1fr;
    content-align: center middle;
}

/* QUEUE VIEW */
#view-queue {
    layout: vertical;
    padding: 1 2;
    height: 1fr;
}

#queue-header-bar {
    layout: horizontal;
    align: left middle;
    margin-bottom: 1;
}

#queue-title {
    text-style: bold;
    color: #ffffff;
    width: 1fr;
}

#queue-table-box {
    height: 1fr;
    border: solid #333333;
    background: #050505;
}

/* FULL PLAYER VIEW */
#view-player {
    layout: vertical;
    align: center middle;
    padding: 2 4;
    height: 1fr;
}

#full-player-box {
    width: 100%;
    height: 100%;
    border: heavy #ffffff;
    background: #050505;
    padding: 1 3;
    layout: vertical;
    align: center middle;
}

#full-ascii {
    content-align: center middle;
    text-style: bold;
    color: #ffffff;
    margin-bottom: 1;
}

#full-title {
    text-style: bold;
    color: #ffffff;
    content-align: center middle;
}

#full-artist {
    color: #888888;
    content-align: center middle;
    margin-bottom: 1;
}

#full-progress {
    content-align: center middle;
    color: #ffffff;
    margin: 1 0;
}

#full-controls {
    layout: horizontal;
    align: center middle;
    margin: 1 0;
}

.player-btn {
    background: #111111;
    color: #ffffff;
    border: solid #444444;
    margin: 0 1;
}

.player-btn:hover {
    background: #ffffff;
    color: #000000;
}

.btn-active {
    border: solid #ffffff;
    background: #222222;
    color: #ffffff;
}

#full-lyrics-box {
    height: 1fr;
    border: solid #222222;
    background: #080808;
    padding: 1;
    margin-top: 1;
}

#full-lyrics-text {
    content-align: center middle;
    height: 1fr;
}

/* DATA TABLES */
DataTable {
    height: 1fr;
    background: #050505;
}

DataTable > .datatable--header {
    text-style: bold;
    background: #111111;
    color: #ffffff;
}

DataTable > .datatable--cursor {
    background: #ffffff;
    color: #000000;
    text-style: bold;
}

/* PLAYER FOOTER BAR */
#player-bar {
    height: 4;
    background: #111111;
    border-top: solid #ffffff;
    padding: 0 2;
    layout: vertical;
    content-align: center middle;
}

#player-bar:hover {
    background: #222222;
}

#player-track {
    text-style: bold;
    color: #ffffff;
}

#player-controls {
    color: #888888;
}
"""

class TrainyApp(App):
    CSS = CSS
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "nav_home", "Home"),
        ("2", "nav_queue", "Queue"),
        ("3", "nav_player", "Player"),
        ("f", "nav_player", "Player"),
        ("/", "focus_search", "Search"),
        ("space", "toggle_playback", "Play/Pause"),
        ("n", "next_track", "Next"),
        ("p", "prev_track", "Prev"),
        ("s", "toggle_shuffle", "Shuffle"),
        ("r", "toggle_smart_radio", "Smart Radio"),
        ("right", "seek_forward", "Skip +10s"),
        ("left", "seek_backward", "Skip -10s"),
        ("period", "seek_forward", "Skip +10s"),
        ("comma", "seek_backward", "Skip -10s"),
    ]

    def __init__(self):
        super().__init__()
        self.api = TrainyAPI()
        self.player = AudioPlayer()
        self.player.on_track_end_callback = self.action_next_track
        
        self.tracks = []
        self.queue = []
        self.queue_index = -1
        self.lyrics = []
        self.lyric_index = -1
        self.shuffle_mode = False
        self.smart_radio_mode = True
        
        # Animations & Visualizers
        self.bar_chars = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_idx = 0
        self.is_loading_track = False
        self.loading_track_title = ""

    def compose(self) -> ComposeResult:
        with Container(id="top-nav-bar"):
            yield Label("TRAINY TUI", id="brand-label")
            with Horizontal(id="nav-buttons-container"):
                yield Button("Home (1)", id="nav-btn-home", classes="nav-btn nav-btn-active")
                yield Button("Queue (2)", id="nav-btn-queue", classes="nav-btn")
                yield Button("Player (3/F)", id="nav-btn-player", classes="nav-btn")

        with ContentSwitcher(initial="view-home", id="main-content-switcher"):
            # VIEW 1: HOME & SEARCH
            with Vertical(id="view-home"):
                yield Input(placeholder="Search songs or paste YouTube Playlist link... (Press / to focus, Enter to search)", id="search-input")
                with Horizontal(id="home-split"):
                    with Vertical(id="tracks-panel"):
                        yield DataTable(id="tracks-table")
                    with Vertical(id="lyrics-side-panel"):
                        yield Label("Synced Lyrics", id="lyrics-side-title")
                        yield Static("Search and play a song to view lyrics...", id="lyrics-side-text")

            # VIEW 2: QUEUE VIEW
            with Vertical(id="view-queue"):
                with Horizontal(id="queue-header-bar"):
                    yield Label("UP NEXT / PLAYBACK QUEUE", id="queue-title")
                    yield Button("Smart Radio: ON", id="btn-toggle-radio", classes="nav-btn nav-btn-active")
                    yield Button("Clear Queue", id="btn-clear-queue", classes="nav-btn")
                with Container(id="queue-table-box"):
                    yield DataTable(id="queue-table")

            # VIEW 3: FULL PLAYER VIEW
            with Vertical(id="view-player"):
                with Vertical(id="full-player-box"):
                    yield Label("┌──────────────────────────────────────────┐\n│  [ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ] │\n└──────────────────────────────────────────┘", id="full-ascii")
                    yield Label("No Track Playing", id="full-title")
                    yield Label("Select a song to play", id="full-artist")
                    yield Label("[────────────────────] 00:00 / 00:00", id="full-progress")
                    
                    with Horizontal(id="full-controls"):
                        yield Button("-10s (<-)", id="btn-p-rewind", classes="player-btn")
                        yield Button("Prev (P)", id="btn-p-prev", classes="player-btn")
                        yield Button("Play/Pause", id="btn-p-toggle", classes="player-btn")
                        yield Button("Next (N)", id="btn-p-next", classes="player-btn")
                        yield Button("+10s (->)", id="btn-p-ff", classes="player-btn")
                        yield Button("Shuffle: OFF", id="btn-p-shuffle", classes="player-btn")
                        yield Button("Smart Radio: ON", id="btn-p-radio", classes="player-btn btn-active")
                        yield Button("Back to Home", id="btn-p-back", classes="player-btn")

                    with Container(id="full-lyrics-box"):
                        yield Static("Synced lyrics will scroll here live...", id="full-lyrics-text")

        with Container(id="player-bar"):
            yield Label("Stopped", id="player-track")
            yield Label("Click bar/F: Player | 1: Home | 2: Queue | Space: Pause | Left/Right: Skip 10s | S: Shuffle | R: Smart Radio | Q: Quit", id="player-controls")

        yield Footer()

    def on_mount(self) -> None:
        stable = self.query_one("#tracks-table", DataTable)
        stable.cursor_type = "row"
        stable.add_columns("Title", "Artist", "Duration")

        qtable = self.query_one("#queue-table", DataTable)
        qtable.cursor_type = "row"
        qtable.add_columns("#", "Title", "Artist", "Duration")

        # Fast 100ms interval for fluid visualizer & loading transition animations
        self.set_interval(0.1, self.update_ticks)

    # NAVIGATION ACTIONS
    def switch_view(self, view_id: str):
        switcher = self.query_one("#main-content-switcher", ContentSwitcher)
        switcher.current = view_id
        
        for btn_id, v_id in [("nav-btn-home", "view-home"), ("nav-btn-queue", "view-queue"), ("nav-btn-player", "view-player")]:
            btn = self.query_one(f"#{btn_id}", Button)
            if v_id == view_id:
                btn.add_class("nav-btn-active")
            else:
                btn.remove_class("nav-btn-active")

    def action_nav_home(self) -> None:
        self.switch_view("view-home")

    def action_nav_queue(self) -> None:
        self.switch_view("view-queue")

    def action_nav_player(self) -> None:
        self.switch_view("view-player")

    def on_click(self, event) -> None:
        widget = event.widget
        if widget and (widget.id in ["player-bar", "player-track", "player-controls"] or widget.parent.id == "player-bar"):
            self.action_nav_player()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid in ["nav-btn-home", "btn-p-back"]:
            self.action_nav_home()
        elif bid == "nav-btn-queue":
            self.action_nav_queue()
        elif bid == "nav-btn-player":
            self.action_nav_player()
        elif bid == "btn-p-toggle":
            self.action_toggle_playback()
        elif bid == "btn-p-next":
            self.action_next_track()
        elif bid == "btn-p-prev":
            self.action_prev_track()
        elif bid == "btn-p-ff":
            self.action_seek_forward()
        elif bid == "btn-p-rewind":
            self.action_seek_backward()
        elif bid == "btn-p-shuffle":
            self.action_toggle_shuffle()
        elif bid in ["btn-toggle-radio", "btn-p-radio"]:
            self.action_toggle_smart_radio()
        elif bid == "btn-clear-queue":
            self.clear_queue()

    def action_focus_search(self) -> None:
        self.action_nav_home()
        self.query_one("#search-input", Input).focus()

    def action_toggle_playback(self) -> None:
        if self.player.process:
            self.player.toggle_pause()
            status = "Paused" if self.player.is_paused else "Playing"
            if self.player.current_track:
                radio_str = " [Radio]" if self.smart_radio_mode else ""
                msg = f"{status}: {self.player.current_track['title']} - {self.player.current_track['artist']}{radio_str}"
                self.query_one("#player-track", Label).update(msg)

    def action_seek_forward(self) -> None:
        if self.player.process:
            self.player.seek(10.0)
            self.notify("Skipped +10s", severity="information")

    def action_seek_backward(self) -> None:
        if self.player.process:
            self.player.seek(-10.0)
            self.notify("Skipped -10s", severity="information")

    def action_toggle_shuffle(self) -> None:
        self.shuffle_mode = not self.shuffle_mode
        status = "ON" if self.shuffle_mode else "OFF"
        self.notify(f"Shuffle Mode: {status}", severity="information")

        btn = self.query_one("#btn-p-shuffle", Button)
        btn.label = f"Shuffle: {'ON' if self.shuffle_mode else 'OFF'}"
        if self.shuffle_mode:
            btn.add_class("btn-active")
        else:
            btn.remove_class("btn-active")

    def action_toggle_smart_radio(self) -> None:
        self.smart_radio_mode = not self.smart_radio_mode
        lbl = "Smart Radio: ON" if self.smart_radio_mode else "Smart Radio: OFF"
        self.notify(f"Smart Radio Autoplay: {'ON' if self.smart_radio_mode else 'OFF'}", severity="information")

        for b_id in ["#btn-toggle-radio", "#btn-p-radio"]:
            btn = self.query_one(b_id, Button)
            btn.label = lbl
            if self.smart_radio_mode:
                btn.add_class("nav-btn-active" if "toggle" in b_id else "btn-active")
            else:
                btn.remove_class("nav-btn-active" if "toggle" in b_id else "btn-active")

    def action_next_track(self) -> None:
        if not self.queue:
            return

        if self.shuffle_mode:
            next_idx = random.randint(0, len(self.queue) - 1)
            self.play_queue_index(next_idx)
        else:
            if self.queue_index < len(self.queue) - 1:
                self.play_queue_index(self.queue_index + 1)
            elif self.smart_radio_mode and self.player.current_track:
                self.notify("Smart Radio: Fetching recommended songs...", severity="information")
                self.fetch_and_append_recommendations(self.player.current_track['videoId'])
            else:
                self.play_queue_index(0)

    @work(exclusive=True)
    async def fetch_and_append_recommendations(self, video_id: str):
        related = await asyncio.to_thread(self.api.get_related_tracks, video_id, 15)
        if related:
            start_idx = len(self.queue)
            self.queue.extend(related)
            self.update_queue_table()
            self.notify(f"Added {len(related)} recommended tracks to Queue", severity="information")
            self.play_queue_index(start_idx)
        else:
            self.play_queue_index(0)

    def action_prev_track(self) -> None:
        if not self.queue:
            return
        next_idx = (self.queue_index - 1) % len(self.queue)
        self.play_queue_index(next_idx)

    # SEARCH & QUEUE LOGIC
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        
        if self.api.is_playlist_url(query):
            self.query_one("#player-track", Label).update("Loading YouTube playlist...")
            self.perform_load_playlist(query)
        else:
            self.query_one("#player-track", Label).update(f"Searching for '{query}'...")
            self.perform_search(query)

    @work(exclusive=True)
    async def perform_load_playlist(self, query: str):
        tracks = await asyncio.to_thread(self.api.get_playlist_tracks, query, 100)
        self.tracks = tracks
        
        table = self.query_one("#tracks-table", DataTable)
        table.clear()
        
        for trk in tracks:
            table.add_row(trk['title'], trk['artist'], trk['duration'])
            
        if tracks:
            self.queue = list(tracks)
            self.notify(f"Loaded Playlist: {len(tracks)} tracks ready!", severity="information")
            self.play_queue_index(0)
        else:
            self.query_one("#player-track", Label).update("Could not load playlist tracks.")

    @work(exclusive=True)
    async def perform_search(self, query: str):
        tracks = await asyncio.to_thread(self.api.search_tracks, query, 20)
        self.tracks = tracks
        
        table = self.query_one("#tracks-table", DataTable)
        table.clear()
        
        for trk in tracks:
            table.add_row(trk['title'], trk['artist'], trk['duration'])
            
        if tracks:
            self.query_one("#player-track", Label).update(f"Found {len(tracks)} tracks. Press Enter to play.")
            table.focus()
        else:
            self.query_one("#player-track", Label).update("No tracks found.")

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "tracks-table":
            idx = event.cursor_row
            if 0 <= idx < len(self.tracks):
                self.queue = list(self.tracks)
                self.play_queue_index(idx)
        elif event.data_table.id == "queue-table":
            idx = event.cursor_row
            if 0 <= idx < len(self.queue):
                self.play_queue_index(idx)

    def update_queue_table(self):
        qtable = self.query_one("#queue-table", DataTable)
        qtable.clear()
        for idx, trk in enumerate(self.queue):
            status_prefix = "> " if idx == self.queue_index else f"{idx+1}."
            qtable.add_row(status_prefix, trk['title'], trk['artist'], trk['duration'])

    def clear_queue(self):
        self.queue = []
        self.queue_index = -1
        self.update_queue_table()
        self.notify("Queue cleared", severity="information")

    def play_queue_index(self, index: int):
        if 0 <= index < len(self.queue):
            self.queue_index = index
            self.update_queue_table()
            track = self.queue[index]
            self.play_track_async(track)

    @work(exclusive=True)
    async def play_track_async(self, track: dict):
        # 1. Trigger Loading Transition State & Spinner Animation
        self.is_loading_track = True
        self.loading_track_title = track['title']
        self.query_one("#full-title", Label).update(f"Loading: {track['title']}...")
        self.query_one("#full-artist", Label).update(f"Artist: {track['artist']}")

        # 2. Extract Audio Stream URL asynchronously
        stream_url = await asyncio.to_thread(self.api.get_stream_url, track['videoId'])
        
        if not stream_url:
            self.is_loading_track = False
            self.query_one("#player-track", Label).update(f"Error loading: {track['title']}")
            self.query_one("#full-title", Label).update(f"Error Loading Stream: {track['title']}")
            return

        # 3. Start Playback & End Loading Transition
        if self.player.play(stream_url, track):
            self.is_loading_track = False
            radio_str = " [Radio]" if self.smart_radio_mode else ""
            self.query_one("#player-track", Label).update(f"> {track['title']} - {track['artist']}{radio_str}")
            
            self.query_one("#full-title", Label).update(track['title'])
            self.query_one("#full-artist", Label).update(track['artist'])

            # 4. Fetch Lyrics asynchronously without blocking audio
            self.lyrics = await asyncio.to_thread(
                self.api.get_synced_lyrics, track['title'], track['artist']
            )
            self.lyric_index = -1
            if not self.lyrics:
                no_lyr = "No synced lyrics found."
                self.query_one("#lyrics-side-text", Static).update(no_lyr)
                self.query_one("#full-lyrics-text", Static).update(no_lyr)
        else:
            self.is_loading_track = False
            self.query_one("#player-track", Label).update("Playback error")

    def update_ticks(self) -> None:
        self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
        spin_char = self.spinner_frames[self.spinner_idx]

        # 1. Loading Track Transition State Animation
        if self.is_loading_track:
            msg = f"{spin_char} Loading Audio Stream: {self.loading_track_title}..."
            self.query_one("#player-track", Label).update(msg)
            
            load_wave = f"{spin_char} ~ ~ ~ LOADING AUDIO STREAM ~ ~ ~ {spin_char}"
            self.query_one("#full-ascii", Label).update(
                f"┌──────────────────────────────────────────┐\n│  [ {load_wave} ]  │\n└──────────────────────────────────────────┘"
            )
            return

        # 2. Live Audio Playing State - Animated Beat Bars Visualizer
        if self.player.is_playing() and not self.player.is_paused:
            dancing_bars = " ".join([random.choice(self.bar_chars) for _ in range(18)])
            self.query_one("#full-ascii", Label).update(
                f"┌──────────────────────────────────────────┐\n│  [ {dancing_bars} ] │\n└──────────────────────────────────────────┘"
            )
        else:
            self.query_one("#full-ascii", Label).update(
                "┌──────────────────────────────────────────┐\n│  [ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ▄ ] │\n└──────────────────────────────────────────┘"
            )

        if not self.player.process or not self.player.current_track:
            return

        elapsed = self.player.get_elapsed_seconds()
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        dur = self.player.current_track.get('duration', '00:00')
        
        status = "Paused" if self.player.is_paused else "Playing"
        title = self.player.current_track['title']
        artist = self.player.current_track['artist']
        radio_str = " [Radio]" if self.smart_radio_mode else ""
        
        time_str = f"[{mins:02d}:{secs:02d} / {dur}]"
        self.query_one("#player-track", Label).update(f"{status}: {title} - {artist}{radio_str}  {time_str}")

        try:
            d_parts = dur.split(':')
            total_sec = int(d_parts[0]) * 60 + int(d_parts[1]) if len(d_parts) == 2 else 180
        except Exception:
            total_sec = 180

        bar_len = 20
        ratio = min(1.0, elapsed / max(1.0, total_sec))
        filled = int(ratio * bar_len)
        bar_str = "█" * filled + "░" * (bar_len - filled)
        self.query_one("#full-progress", Label).update(f"[{bar_str}]  {mins:02d}:{secs:02d} / {dur}")

        if not self.lyrics:
            return

        active_i = -1
        for i, line in enumerate(self.lyrics):
            if elapsed >= line['time']:
                active_i = i
            else:
                break

        if active_i != self.lyric_index and active_i != -1:
            self.lyric_index = active_i
            lines = []
            start_i = max(0, active_i - 3)
            end_i = min(len(self.lyrics), active_i + 4)

            for i in range(start_i, end_i):
                txt = self.lyrics[i]['text']
                if i == active_i:
                    lines.append(f"[bold white]> {txt}[/bold white]")
                else:
                    lines.append(f"[dim]{txt}[/dim]")

            formatted = "\n\n".join(lines)
            self.query_one("#lyrics-side-text", Static).update(formatted)
            self.query_one("#full-lyrics-text", Static).update(formatted)

    def on_unmount(self) -> None:
        self.player.stop()

if __name__ == "__main__":
    app = TrainyApp()
    app.run()
