-- extras/fortune.lua — decorative, not wired into the app.
-- a tiny fortune-cookie script, sitting here mostly so the Scripts/Lua tab
-- has something native to point at. run with: lua fortune.lua

local fortunes = {
	"lossless или ничего.",
	"320kbps -- это не lossless, не обманывай себя.",
	"обложка важнее битрейта.",
	"stylua лучше форматирует lua, чем ты руками.",
	"made by savsis with <3",
}

math.randomseed(os.time())
print(fortunes[math.random(#fortunes)])
