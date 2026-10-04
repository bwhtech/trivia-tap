import { io } from "socket.io-client";
import { socketio_port } from "../../../../sites/common_site_config.json";

export function initSocket() {
	const host = window.location.hostname;
	const siteName = window.site_name || host;
	const port = window.location.port ? `:${socketio_port}` : "";
	const protocol = port ? "http" : "https";
	const url = `${protocol}://${host}${port}/${siteName}`;

	// no attempt cap: giving up strands the screen on the 20s resync watchdog for the rest of the game
	return io(url, { withCredentials: true });
}
