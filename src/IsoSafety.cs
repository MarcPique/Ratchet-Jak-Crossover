using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
internal static class DiscSafety {
    internal static readonly JavaScriptSerializer Json = new JavaScriptSerializer { MaxJsonLength = Int32.MaxValue };
    internal const string NativeTarget = "x86_64-pc-windows-msvc";
    internal const long GiB = 1024L * 1024L * 1024L;
    internal static string Full(string value) {
        if (String.IsNullOrWhiteSpace(value)) throw new IOException("Falta una ruta.");
        if (!Path.IsPathRooted(value) || value.StartsWith(@"\\")) throw new IOException("Usa una ruta absoluta en un disco local: " + value);
        return Path.GetFullPath(value).TrimEnd(Path.DirectorySeparatorChar);
    }
    internal static bool Within(string path, string root) {
        path = Full(path); root = Full(root);
        return path.Equals(root, StringComparison.OrdinalIgnoreCase) || path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);
    }
    internal static void NoLinks(string path) {
        string current = Full(path);
        while (!String.IsNullOrEmpty(current)) {
            if ((File.Exists(current) || Directory.Exists(current)) && (File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
                throw new IOException("No se permiten enlaces/junctions en las entradas o el destino: " + current);
            DirectoryInfo parent = Directory.GetParent(current);
            current = parent == null ? null : parent.FullName;
        }
    }
    // Win32 argv quoting, used only with CreateProcess / UseShellExecute=false, never cmd.exe.
    internal static string Quote(string value) {
        if (value.IndexOf('\0') >= 0 || value.IndexOf('\r') >= 0 || value.IndexOf('\n') >= 0) throw new IOException("Argumento inválido.");
        StringBuilder result = new StringBuilder("\""); int slashes = 0;
        foreach (char ch in value) {
            if (ch == '\\') { slashes++; continue; }
            if (ch == '"') { result.Append('\\', slashes * 2 + 1).Append(ch); slashes = 0; continue; }
            result.Append('\\', slashes).Append(ch); slashes = 0;
        }
        return result.Append('\\', slashes * 2).Append('"').ToString();
    }
    internal static byte[] ReadAt(FileStream stream, long offset, int count) {
        if (offset < 0 || count < 0 || offset > stream.Length - count) throw new IOException("ISO truncada o extent fuera de la imagen.");
        byte[] bytes = new byte[count]; stream.Position = offset; int done = 0;
        while (done < count) { int n = stream.Read(bytes, done, count - done); if (n == 0) throw new IOException("ISO truncada."); done += n; }
        return bytes;
    }
    internal static uint Le32(byte[] data, int at) { return BitConverter.ToUInt32(data, at); }
    internal static byte[] IsoRootFile(string image, string name) {
        using (FileStream stream = File.Open(image, FileMode.Open, FileAccess.Read, FileShare.Read)) {
            byte[] pvd = null;
            for (int sector = 16; sector < 64; sector++) {
                byte[] descriptor = ReadAt(stream, sector * 2048L, 2048);
                if (Encoding.ASCII.GetString(descriptor, 1, 5) != "CD001") throw new IOException("Se necesita una ISO9660 de PS2 de sectores de 2048 bytes; CHD/BIN/PS3 no son compatibles.");
                if (descriptor[0] == 1) { pvd = descriptor; break; }
                if (descriptor[0] == 255) break;
            }
            if (pvd == null || pvd[156] < 34) throw new IOException("No existe directorio raíz ISO9660.");
            uint rootLength = Le32(pvd, 166);
            if (rootLength == 0 || rootLength > 16 * 1024 * 1024) throw new IOException("Directorio ISO9660 inválido.");
            byte[] directory = ReadAt(stream, Le32(pvd, 158) * 2048L, (int)rootLength);
            for (int at = 0; at < directory.Length;) {
                int length = directory[at];
                if (length == 0) { at = ((at / 2048) + 1) * 2048; continue; }
                if (length < 34 || at + length > directory.Length || directory[at + 32] > length - 33) throw new IOException("Registro ISO9660 inválido.");
                string entry = Encoding.ASCII.GetString(directory, at + 33, directory[at + 32]).Split(';')[0];
                if (entry.Equals(name, StringComparison.OrdinalIgnoreCase)) {
                    uint size = Le32(directory, at + 10);
                    if (size > 4 * 1024 * 1024) throw new IOException("Archivo de identificación de disco demasiado grande.");
                    return ReadAt(stream, Le32(directory, at + 2) * 2048L, (int)size);
                }
                at += length;
            }
            throw new IOException("No se encuentra " + name + " en la ISO.");
        }
    }
    internal static string DiscBoot(string image) {
        string cnf = Encoding.ASCII.GetString(IsoRootFile(image, "SYSTEM.CNF"));
        Match match = Regex.Match(cnf, @"(?im)^\s*BOOT2\s*=\s*cdrom0:\\+([A-Z]{4}[_-][0-9]{3}\.[0-9]{2})(?:;1)?\s*$");
        if (!match.Success) throw new IOException("SYSTEM.CNF no contiene un BOOT2 PS2 reconocido.");
        return match.Groups[1].Value.ToUpperInvariant();
    }
    internal static long TreeBytes(string root) {
        NoLinks(root); long total = 0;
        foreach (string file in Directory.GetFiles(root)) { NoLinks(file); total = checked(total + new FileInfo(file).Length); }
        foreach (string dir in Directory.GetDirectories(root)) total = checked(total + TreeBytes(dir));
        return total;
    }
}
