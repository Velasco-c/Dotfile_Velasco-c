-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
-- HYPRLAND CONFIGURATION - Velasco-c              --
-- CachyOS / Hyprland 0.56 / Lua                   --
-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
-- Referencia: https://wiki.hypr.land/Configuring/Start/


-----------------
---- THEME ----
-----------------

-- Colores generados por Noctalia a partir del wallpaper (no editar noctalia.lua a mano).
-- Noctalia crea ~/.config/hypr/noctalia.lua al arrancar; si aún no existe, Hyprland usa un color de respaldo
-- en vez de entrar en modo de emergencia.
local noctalia_ok, noctalia = pcall(require, "noctalia")
local theme = noctalia_ok and noctalia.colors or { surface = "rgb(1e1e2e)" }


------------------
---- MONITORS ----
------------------

-- output = "" aplica a todas las pantallas.
-- Escala 1.2: si Steam se ve borroso, mantén force_zero_scaling (ver XWAYLAND).
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = 1.2,
})


---------------------
---- MY PROGRAMS ----
---------------------

local terminal    = "kitty"
local fileManager = "dolphin"
local menu        = "noctalia msg panel-open launcher"


-------------------
---- AUTOSTART ----
-------------------

hl.on("hyprland.start", function()
    hl.exec_cmd("noctalia")
end)


-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XCURSOR_THEME", "Skyrim-by-ru5tyshark-cursors")


-----------------------
----- PERMISSIONS -----
-----------------------

-- Ejemplos (descomenta si los necesitas):
-- hl.config({ ecosystem = { enforce_permissions = true } })
-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")


-----------------------
---- LOOK AND FEEL ----
-----------------------

hl.config({
    general = {
        gaps_in  = 5,
        gaps_out = 20,

        border_size = 1,

        -- Los colores de los bordes vienen de Noctalia (apply_theme al final del archivo)

        resize_on_border = false,
        allow_tearing = false,
        layout = "dwindle",
    },

    decoration = {
        rounding       = 10,
        rounding_power = 2,

        active_opacity   = 1.0,
        inactive_opacity = 1.0,

        shadow = {
            enabled      = true,
            range        = 4,
            render_power = 3,
            -- Color "surface" de Noctalia con la misma opacidad de antes (ee)
            color        = (theme.surface:gsub("rgb%((%x+)%)", "rgba(%1ee)")),
        },

        blur = {
            enabled           = true,
            size              = 2,
            passes            = 2,
            vibrancy          = 0.35,
            new_optimizations = true,
            ignore_opacity    = false,
        },
    },

    animations = {
        enabled = true,
    },
})


-------------------
---- ANIMATIONS ----
-------------------

hl.curve("easeOutQuint", {
    type = "bezier",
    points = { {0.23, 1}, {0.32, 1} }
})

hl.curve("easeInOutCubic", {
    type = "bezier",
    points = { {0.65, 0.05}, {0.36, 1} }
})

hl.curve("linear", {
    type = "bezier",
    points = { {0, 0}, {1, 1} }
})

hl.curve("almostLinear", {
    type = "bezier",
    points = { {0.5, 0.5}, {0.75, 1} }
})

hl.curve("quick", {
    type = "bezier",
    points = { {0.15, 0}, {0.1, 1} }
})

-- Spring por defecto
hl.curve("easy", {
    type = "spring",
    mass = 1,
    stiffness = 238.1191,
    dampening = 24.21279333
})

hl.animation({ leaf = "global",      enabled = true, speed = 10,   bezier = "default" })
hl.animation({ leaf = "border",      enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",     enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn",   enabled = true, speed = 4.1,  spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut",  enabled = true, speed = 1.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "fadeIn",      enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut",     enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade",        enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers",      enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn",    enabled = true, speed = 4,    bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut",   enabled = true, speed = 1.5,  bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn",  enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces",  enabled = true, speed = 4,    bezier = "easeOutQuint", style = "slidefade 20%" })
hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 4, bezier = "easeOutQuint", style = "slidefade 20%" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 4, bezier = "easeOutQuint", style = "slidefade 20%" })


---------------------------
---- WORKSPACE SETTINGS ----
---------------------------

hl.config({
    dwindle = {
        preserve_split = true,
    },
})

hl.config({
    master = {
        new_status = "master",
    },
})

hl.config({
    scrolling = {
        fullscreen_on_one_column = true,
    },
})


----------------
----  MISC  ----
----------------

hl.config({
    misc = {
        force_default_wallpaper = -1,
        disable_hyprland_logo   = false,
    },
})

-- XWAYLAND: Steam y apps X11 se ven nítidos aunque la escala no sea 1
hl.config({
    xwayland = {
        force_zero_scaling = true,
    },
})


---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout    = "es",
        kb_variant   = "",
        kb_model     = "pc105",
        kb_options   = "",
        kb_rules     = "",
        follow_mouse = 1,
        sensitivity  = 0,
        touchpad = {
            natural_scroll = false,
        },
    },
})


----------------
---- GESTURES ----
----------------

hl.gesture({ fingers = 3, direction = "vertical",   action = "workspace" })
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })


---------------------
---- DEVICES --------
---------------------

hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})


---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER"

------------------------------------------------
-- APPLICATIONS
------------------------------------------------

-- SUPER + Q: terminal (Kitty con Fish)
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal), { description = "Open Kitty terminal" })

-- SUPER + W: Alacritty con Bash
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("alacritty"), { description = "Open Alacritty terminal" })

-- SUPER + E: Dolphin
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager), { description = "Open Dolphin file manager" })

-- SUPER + R: launcher de Noctalia
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu), { description = "Open application launcher" })

-- SUPER + D: bloquear pantalla
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("noctalia msg session lock"), { description = "Lock screen" })


------------------------------------------------
-- WINDOW MANAGEMENT
------------------------------------------------

hl.bind(mainMod .. " + C",   hl.dsp.window.close(),                          { description = "Close active window" })
hl.bind("ALT + F4",          hl.dsp.window.close(),                          { description = "Close active window" })
hl.bind(mainMod .. " + A",   hl.dsp.window.float({ action = "toggle" }),     { description = "Toggle floating window" })
hl.bind(mainMod .. " + F",   hl.dsp.window.fullscreen({ action = "toggle" }), { description = "Toggle fullscreen" })
hl.bind(mainMod .. " + P",   hl.dsp.window.pseudo(),                         { description = "Toggle pseudo tiling" })
hl.bind(mainMod .. " + J",   hl.dsp.layout("togglesplit"),                   { description = "Toggle split" })


------------------------------------------------
-- WINDOW FOCUS
------------------------------------------------

hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }),  { description = "Focus window left" })
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }), { description = "Focus window right" })
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }),    { description = "Focus window up" })
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }),  { description = "Focus window down" })

-- ALT + TAB: ciclar ventanas (tu atajo; el selector de Noctalia no se usa para no duplicar)
hl.bind("ALT + TAB", hl.dsp.window.cycle_next(), { description = "Switch to next window" })


------------------------------------------------
-- HYPRSPACE OVERVIEW
------------------------------------------------

-- SUPER + TAB: vista general de workspaces (plugin Hyprspace)
hl.bind("SUPER + TAB", function()
    hl.plugin.overview.toggle()
end, { description = "Toggle Hyprspace overview" })


------------------------------------------------
-- NOCTALIA
------------------------------------------------

hl.bind("ALT + P",           hl.dsp.exec_cmd("noctalia msg screenshot-region"),     { description = "Take region screenshot" })
hl.bind("ALT + SHIFT + P",   hl.dsp.exec_cmd("noctalia msg screenshot-fullscreen"), { description = "Take fullscreen screenshot" })
hl.bind("ALT + N",           hl.dsp.exec_cmd("noctalia msg media play-pause"),      { description = "Play or pause media" })
hl.bind("ALT + M",           hl.dsp.exec_cmd("noctalia msg media next"),            { description = "Next media track" })
hl.bind("ALT + B",           hl.dsp.exec_cmd("noctalia msg media previous"),        { description = "Previous media track" })
hl.bind("ALT + S",           hl.dsp.exec_cmd("noctalia msg panel-open control-center"), { description = "Open Noctalia control center" })


------------------------------------------------
-- WORKSPACES
------------------------------------------------

-- SUPER + 1..4: cambiar workspace / SUPER + SHIFT + 1..4: mover ventana
for i = 1, 4 do
    local key = tostring(i)

    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }),
        { description = "Switch to workspace " .. i })

    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }),
        { description = "Move window to workspace " .. i })
end

-- ALT + Q / ALT + W: workspace anterior / siguiente
hl.bind("ALT + Q", hl.dsp.focus({ workspace = "e-1" }), { description = "Previous workspace" })
hl.bind("ALT + W", hl.dsp.focus({ workspace = "e+1" }), { description = "Next workspace" })

-- SUPER + rueda del mouse: cambiar workspace
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))


------------------------------------------------
-- SPECIAL WORKSPACE / SCRATCHPAD
------------------------------------------------

hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"),
    { description = "Toggle special workspace" })

hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }),
    { description = "Move window to special workspace" })


------------------------------------------------
-- MOUSE WINDOW MANAGEMENT
------------------------------------------------

hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })


------------------------------------------------
-- SESSION
------------------------------------------------

-- SUPER + SHIFT + M: salir de Hyprland
hl.bind(mainMod .. " + SHIFT + M",
    hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch 'hl.dsp.exit()'"),
    { description = "Shutdown Hyprland" })


------------------------------------------------
-- AUDIO, BRILLO Y MEDIA
------------------------------------------------

hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"),
    { locked = true, repeating = true, description = "Increase volume" })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
    { locked = true, repeating = true, description = "Decrease volume" })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
    { locked = true, repeating = true, description = "Mute audio" })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
    { locked = true, repeating = true, description = "Mute microphone" })

hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),
    { locked = true, repeating = true, description = "Increase brightness" })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),
    { locked = true, repeating = true, description = "Decrease brightness" })

hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),         { locked = true, description = "Next media track" })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),     { locked = true, description = "Previous media track" })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"),   { locked = true, description = "Play media" })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"),   { locked = true, description = "Pause media" })


--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

------------------------------------------------
-- WORKSPACES PERSISTENTES
-- Cambia "eDP-1" por el nombre de tu pantalla (hyprctl monitors)
------------------------------------------------

hl.workspace_rule({ workspace = "1", monitor = "eDP-1", persistent = true })
hl.workspace_rule({ workspace = "2", monitor = "eDP-1", persistent = true })
hl.workspace_rule({ workspace = "3", monitor = "eDP-1", persistent = true })
hl.workspace_rule({ workspace = "4", monitor = "eDP-1", persistent = true })


------------------------------------------------
-- CAPAS DE NOCTALIA (blur en barra, notificaciones y paneles)
------------------------------------------------

hl.layer_rule({
    name = "noctalia",
    match = {
        namespace = "^noctalia-(bar-.+|notification|dock|panel|attached-panel|osd|window-switcher)$",
    },
    no_anim = true,
    ignore_alpha = 0.5,
    blur = true,
    blur_popups = true,
})


------------------------------------------------
-- REGLAS DE VENTANAS
------------------------------------------------

-- Transparencia y esquinas para tus apps
hl.window_rule({
    name = "dolphin-glass",
    match = { class = "^org\\.kde\\.dolphin$" },
    opacity = "0.85 override 0.85 override 0.85 override",
    rounding = 10,
})

hl.window_rule({
    name = "vscode-glass",
    match = { class = "(?i)^(com\\.microsoft\\.vscode|code(-oss)?)$" },
    opacity = "0.85 override 0.85 override 0.9 override",
    rounding = 10,
})

hl.window_rule({
    name = "firefox-dev-glass",
    match = { class = "^firefox-dev$" },
    opacity = "0.92 override 0.92 override 0.92 override",
    rounding = 10,
})

hl.window_rule({
    name = "brave-glass",
    match = { class = "^(brave-browser|brave)$" },
    opacity = "1 override 1 override 1 override",
    rounding = 10,
})

hl.window_rule({
    name = "alacritty-glass",
    match = { class = "^Alacritty$" },
    opacity = "0.8 override 0.8 override 0.8 override",
    rounding = 10,
})

hl.window_rule({
    name = "kitty-glass",
    match = { class = "^kitty$" },
    opacity = "0.8 override 0.8 override 0.8 override",
    rounding = 10,
})

-- Evitar eventos de maximizar (tu configuración actual)
hl.window_rule({
    name = "suppress-maximize-events",
    match = { class = ".*" },
    suppress_event = "maximize",
})

-- Arreglo de arrastres en XWayland
hl.window_rule({
    name = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },
    no_focus = true,
})

-- Ventana de hyprland-run en la esquina
hl.window_rule({
    name = "move-hyprland-run",
    match = { class = "hyprland-run" },
    move  = "20 monitor_h-120",
    float = true,
})

-- Widget de reloj (tty-clock)
hl.window_rule({
    name = "clock-widget",
    match = { class = "^clockwidget$" },
    float = true,
    pin = true,
    no_focus = true,
    border_size = 0,
    size = "500 250",
    move = "1050 60",
})


-- Aplicar los colores de Noctalia (bordes de Hyprland y grupos)
if noctalia_ok then
    noctalia.apply_theme()
end
