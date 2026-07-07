// nexdex.space installer/launcher
//
// the app payload (portable python runtime + full app source, including
// ffmpeg) is embedded inside this exe as a plain RCDATA resource (a zip).
// on first run it dumps that resource to a temp zip file and extracts it
// next to itself via the OS-native tar.exe, then launches the app with the
// bundled python — no system python required at all. embedding as a real
// PE resource (rather than appending the zip after the exe) keeps this a
// normal, well-formed PE, so it can still be Authenticode-signed as usual.

#include <windows.h>
#include <shlobj.h>
#include <shobjidl.h>
#include <objbase.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <filesystem>

namespace fs = std::filesystem;

static void createDesktopShortcut(const fs::path& targetExe) {
    wchar_t* desktopPath = nullptr;
    if (FAILED(SHGetKnownFolderPath(FOLDERID_Desktop, 0, nullptr, &desktopPath))) return;
    fs::path shortcutPath = fs::path(desktopPath) / L"nexdex.space.lnk";
    CoTaskMemFree(desktopPath);

    if (fs::exists(shortcutPath)) return;

    IShellLinkW* shellLink = nullptr;
    if (FAILED(CoCreateInstance(CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER,
                                 IID_IShellLinkW, reinterpret_cast<void**>(&shellLink))))
        return;

    shellLink->SetPath(targetExe.c_str());
    shellLink->SetWorkingDirectory(targetExe.parent_path().c_str());
    shellLink->SetIconLocation(targetExe.c_str(), 0);
    shellLink->SetDescription(L"nexdex.space -- made by savsis");

    IPersistFile* persistFile = nullptr;
    if (SUCCEEDED(shellLink->QueryInterface(IID_IPersistFile, reinterpret_cast<void**>(&persistFile)))) {
        persistFile->Save(shortcutPath.c_str(), TRUE);
        persistFile->Release();
    }
    shellLink->Release();
}

static std::wstring quote(const std::wstring& s) {
    return L"\"" + s + L"\"";
}

static bool runAndWait(const std::wstring& cmdLine) {
    STARTUPINFOW si{};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};

    std::vector<wchar_t> buf(cmdLine.begin(), cmdLine.end());
    buf.push_back(0);

    if (!CreateProcessW(nullptr, buf.data(), nullptr, nullptr, FALSE,
                         CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
        return false;
    }
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return code == 0;
}

static bool extractPayloadResource(const fs::path& outZipPath) {
    HMODULE self = GetModuleHandleW(nullptr);
    HRSRC res = FindResourceW(self, MAKEINTRESOURCEW(102), MAKEINTRESOURCEW(10) /* RT_RCDATA */);
    if (!res) return false;

    HGLOBAL data = LoadResource(self, res);
    if (!data) return false;

    DWORD size = SizeofResource(self, res);
    void* ptr = LockResource(data);
    if (!ptr || size == 0) return false;

    std::ofstream out(outZipPath, std::ios::binary);
    if (!out) return false;
    out.write(static_cast<const char*>(ptr), static_cast<std::streamsize>(size));
    return out.good();
}

static bool runDetached(const std::wstring& cmdLine, const std::wstring& cwd) {
    STARTUPINFOW si{};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};

    std::vector<wchar_t> buf(cmdLine.begin(), cmdLine.end());
    buf.push_back(0);

    BOOL ok = CreateProcessW(nullptr, buf.data(), nullptr, nullptr, FALSE,
                              DETACHED_PROCESS, nullptr, cwd.c_str(), &si, &pi);
    if (!ok) return false;
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return true;
}

int wmain() {
    CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

    wchar_t exePathBuf[MAX_PATH];
    GetModuleFileNameW(nullptr, exePathBuf, MAX_PATH);
    fs::path exePath(exePathBuf);

    wchar_t* localAppData = nullptr;
    SHGetKnownFolderPath(FOLDERID_LocalAppData, 0, nullptr, &localAppData);
    fs::path installDir = fs::path(localAppData) / L"nexdex.space";
    CoTaskMemFree(localAppData);

    fs::path appDir = installDir / L"app";
    fs::path pythonExe = installDir / L"python" / L"pythonw.exe";
    fs::path appPy = appDir / L"app.py";
    fs::path marker = installDir / L".installed";

    std::wcout << L"nexdex.space\n";

    if (!fs::exists(marker)) {
        std::wcout << L"первый запуск -- распаковываю (это займёт немного времени)...\n";
        std::error_code ec;
        fs::create_directories(installDir, ec);

        fs::path tempZip = installDir / L"_payload.zip";
        if (!extractPayloadResource(tempZip)) {
            std::wcerr << L"не удалось прочитать встроенные данные приложения.\n";
            Sleep(4000);
            return 1;
        }

        wchar_t sysDir[MAX_PATH];
        GetSystemDirectoryW(sysDir, MAX_PATH);
        std::wstring tarExe = std::wstring(sysDir) + L"\\tar.exe";

        std::wstring cmd = quote(tarExe) + L" -xf " + quote(tempZip.wstring()) +
                            L" -C " + quote(installDir.wstring());

        bool ok = runAndWait(cmd);
        fs::remove(tempZip, ec);

        if (!ok) {
            std::wcerr << L"ошибка распаковки. попробуй запустить ещё раз или проверь права доступа.\n";
            Sleep(4000);
            return 1;
        }

        std::ofstream(marker.string()).put('1');
        createDesktopShortcut(exePath);
        std::wcout << L"готово -- ярлык добавлен на рабочий стол.\n";
    }

    if (!fs::exists(appPy) || !fs::exists(pythonExe)) {
        std::wcerr << L"файлы приложения повреждены -- удали папку " << installDir.wstring()
                    << L" и запусти установщик заново.\n";
        Sleep(5000);
        return 1;
    }

    std::wcout << L"запускаю...\n";
    std::wstring runCmd = quote(pythonExe.wstring()) + L" " + quote(appPy.wstring());
    if (!runDetached(runCmd, appDir.wstring())) {
        std::wcerr << L"не удалось запустить приложение.\n";
        Sleep(4000);
        return 1;
    }

    Sleep(1200);
    return 0;
}
