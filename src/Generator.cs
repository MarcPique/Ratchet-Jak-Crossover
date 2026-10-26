// Branded offline ISO generator. No retail game resources are embedded.
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
[assembly:AssemblyTitle("Ratchet&Jak — Generador experimental")]
[assembly:AssemblyVersion("0.2.2.0")]
public sealed class Request {
 public string RatchetIso="",JakIso="",Destination="",DesktopDirectory="",Language="";
}
internal static class Generator {
 const string PayloadHash="__PAYLOAD_SHA256__";
 internal static string Inspect(Request c){
  Lang.Select(c.Language);c.Language=Lang.Code;
  c.RatchetIso=DiscSafety.Full(c.RatchetIso);c.JakIso=DiscSafety.Full(c.JakIso);c.Destination=DiscSafety.Full(c.Destination);
  foreach(string path in new[]{c.RatchetIso,c.JakIso,c.Destination})DiscSafety.NoLinks(path);
  if(!Environment.Is64BitOperatingSystem)throw new IOException(Lang.T("Se necesita Windows de 64 bits."));
  if(c.Destination.Length<=3||File.Exists(c.Destination))throw new IOException(Lang.T("Elige una carpeta nueva, no la raíz del disco."));
  if(!Directory.Exists(Path.GetDirectoryName(c.Destination)))throw new IOException(Lang.T("Debe existir la carpeta padre del destino."));
  if(Directory.Exists(c.Destination)&&Directory.EnumerateFileSystemEntries(c.Destination).Any())throw new IOException(Lang.T("El destino debe estar vacío. No se sustituyen instalaciones ni partidas."));
  if(c.RatchetIso.Equals(c.JakIso,StringComparison.OrdinalIgnoreCase))throw new IOException(Lang.T("Selecciona dos ISO distintas."));
  foreach(string iso in new[]{c.RatchetIso,c.JakIso}){
   if(!File.Exists(iso))throw new IOException(Lang.T("No existe la ISO: "+iso));
   if(DiscSafety.Within(iso,c.Destination))throw new IOException(Lang.T("Las ISO deben quedar fuera del destino."));
  }
  string ratchet=DiscSafety.DiscBoot(c.RatchetIso),jak=DiscSafety.DiscBoot(c.JakIso);
  if(ratchet!="SCUS_971.99")throw new IOException(Lang.T("Ratchet requiere NTSC-U SCUS_971.99 v1.00. Detectado: "+ratchet));
  using(var sha=SHA1.Create()){
   string hash=BitConverter.ToString(sha.ComputeHash(DiscSafety.IsoRootFile(c.RatchetIso,"SCUS_971.99"))).Replace("-","").ToLowerInvariant();
   if(hash!="72fd1de379dafd8f243dceeb3be50980f3fd3cd5")throw new IOException(Lang.T("La revisión Ratchet no coincide con v1.00."));
  }
  if(jak!="SCUS_971.24")throw new IOException(Lang.T("Jak requiere The Precursor Legacy NTSC-U SCUS_971.24. Detectado: "+jak));
  long required=checked(3*(new FileInfo(c.RatchetIso).Length+new FileInfo(c.JakIso).Length)+8*DiscSafety.GiB);
  if(new DriveInfo(Path.GetPathRoot(c.Destination)).AvailableFreeSpace<required)throw new IOException(Lang.T("Espacio insuficiente. Reserva estimada: "+(required/DiscSafety.GiB+1)+" GiB."));
  if(String.IsNullOrWhiteSpace(c.DesktopDirectory))c.DesktopDirectory=Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
  c.DesktopDirectory=DiscSafety.Full(c.DesktopDirectory);
  if(!Directory.Exists(c.DesktopDirectory))throw new IOException(Lang.T("No existe la carpeta del escritorio."));
  return Lang.T("Discos compatibles identificados. OpenGOAL y el extractor verificarán el contenido completo.");
 }
 static void Extract(string root,Action<string> line){
  line("FASE: "+Lang.T("Preparar herramientas incluidas"));Directory.CreateDirectory(root);
  using(Stream input=Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip")){
   if(input==null)throw new IOException(Lang.T("Falta el paquete de herramientas."));
   using(var sha=SHA256.Create()){
    string hash=BitConverter.ToString(sha.ComputeHash(input)).Replace("-","").ToLowerInvariant();
    if(hash!=PayloadHash)throw new IOException(Lang.T("El paquete del generador está dañado."));
   }
   input.Position=0;
   using(var zip=new ZipArchive(input,ZipArchiveMode.Read)){
    long total=0;if(zip.Entries.Count>30000)throw new IOException(Lang.T("Paquete inválido."));
    foreach(var entry in zip.Entries){
     if(entry.FullName.EndsWith("/"))continue;
     string path=Path.GetFullPath(Path.Combine(root,entry.FullName));
     if(!DiscSafety.Within(path,root)||Path.IsPathRooted(entry.FullName))throw new IOException(Lang.T("Ruta ZIP inválida."));
     total=checked(total+entry.Length);if(total>2L*DiscSafety.GiB)throw new IOException(Lang.T("Paquete demasiado grande."));
     Directory.CreateDirectory(Path.GetDirectoryName(path));
     using(var source=entry.Open())using(var dest=new FileStream(path,FileMode.CreateNew,FileAccess.Write))source.CopyTo(dest);
    }
   }
  }
 }
 internal static int Build(Request c,Action<string> line){
  line(Inspect(c));Directory.CreateDirectory(c.Destination);
  string baseDir=Path.Combine(c.Destination,".builder"),payload=Path.Combine(baseDir,"payload");
  Extract(payload,line);
  string request=Path.Combine(baseDir,"request.local.json");File.WriteAllText(request,DiscSafety.Json.Serialize(c),new UTF8Encoding(false));
  string temp=Path.Combine(baseDir,"temp");Directory.CreateDirectory(temp);
  var start=new ProcessStartInfo(Path.Combine(payload,@"python\python.exe")){
   WorkingDirectory=baseDir,UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,
   Arguments=String.Join(" ",new[]{"-I","-B","-X","utf8",Path.Combine(payload,@"scripts\generate.py"),"--request",request}.Select(DiscSafety.Quote))
  };
  foreach(string key in new[]{"TEMP","TMP","TMPDIR"})start.EnvironmentVariables[key]=temp;
  start.EnvironmentVariables.Remove("PYTHONHOME");start.EnvironmentVariables.Remove("PYTHONPATH");
  using(var proc=new Process{StartInfo=start}){
   proc.OutputDataReceived+=(s,e)=>{if(e.Data!=null)line(e.Data);};
   proc.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)line(e.Data);};
   proc.Start();proc.BeginOutputReadLine();proc.BeginErrorReadLine();proc.WaitForExit();
   if(proc.ExitCode!=0)throw new IOException(Lang.T("No se completó la generación. Consulta build.log. Se conserva el diagnóstico y no se altera ningún original."));
  }
  return 0;
 }
 [STAThread] static int Main(string[] args){
  try{
   if(args.Length==2&&args[0]=="--build")return Build(DiscSafety.Json.Deserialize<Request>(File.ReadAllText(args[1])),Console.WriteLine);
   if(args.Length==3&&args[0]=="--inspect"){
    try{var c=DiscSafety.Json.Deserialize<Request>(File.ReadAllText(args[1]));string value=Inspect(c);File.WriteAllText(args[2],DiscSafety.Json.Serialize(new{ready=true,note=value,language=c.Language}),new UTF8Encoding(false));return 0;}
    catch(Exception e){File.WriteAllText(args[2],DiscSafety.Json.Serialize(new{ready=false,error=Lang.T(e.Message)}),new UTF8Encoding(false));return 2;}
   }
   Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
   if((args.Length==2||args.Length==3)&&args[0]=="--render-ui"){
    if(args.Length==3)Lang.Select(args[2]);
    using(var form=new GeneratorForm()){form.Show();Application.DoEvents();using(var bmp=new Bitmap(form.Width,form.Height)){form.DrawToBitmap(bmp,new Rectangle(Point.Empty,bmp.Size));bmp.Save(args[1]);}form.Close();}return 0;
   }
   if(args.Length!=0)throw new IOException(Lang.T("Opción desconocida."));
   Application.Run(new GeneratorForm());return 0;
  }catch(Exception e){Console.Error.WriteLine(Lang.T(e.Message));if(args.Length==0)MessageBox.Show(Lang.T(e.Message),"Ratchet&Jak",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1;}
 }
}
internal sealed class GeneratorForm:Form {
 readonly TextBox ratchet=new TextBox(),jak=new TextBox(),destination=new TextBox(),log=new TextBox();
 readonly Panel language=new Panel();readonly Label summary=new Label();
 readonly Button generate=new Button();readonly Label status=new Label();readonly ProgressBar progress=new ProgressBar();bool busy;
 public GeneratorForm(){
  Text=Lang.T("Ratchet&Jak — Generador experimental");ClientSize=new Size(930,765);MinimumSize=new Size(930,800);StartPosition=FormStartPosition.CenterScreen;
  BackColor=Color.FromArgb(15,22,33);ForeColor=Color.White;Font=new Font("Segoe UI",10F);AutoScaleMode=AutoScaleMode.Dpi;
  using(var input=Assembly.GetExecutingAssembly().GetManifestResourceStream("brand.icon"))Icon=new Icon(input);
  var banner=new PictureBox{Left=30,Top=16,Width=860,Height=155,SizeMode=PictureBoxSizeMode.Zoom};
  using(var input=Assembly.GetExecutingAssembly().GetManifestResourceStream("brand.logo"))using(var decoded=Image.FromStream(input))banner.Image=new Bitmap(decoded);Controls.Add(banner);
  Controls.Add(new Label{Left=34,Top=181,Width=180,Height=25,Text="Language / Idioma"});
  language.SetBounds(220,177,670,32);Controls.Add(language);
  for(int i=0;i<Lang.Codes.Length;i++){string code=Lang.Codes[i];var choice=new RadioButton{Left=i*133,Top=1,Width=130,Height=29,Text=Lang.Names[i],Checked=Lang.Code==code};choice.CheckedChanged+=(sender,e)=>{if(choice.Checked){Lang.Select(code);RefreshLanguage();}};language.Controls.Add(choice);}
  summary.SetBounds(34,220,860,60);summary.ForeColor=Color.FromArgb(246,186,84);Controls.Add(summary);
  AddRow("Ratchet & Clank · USA v1.00",ratchet,287,false);AddRow("Jak and Daxter · USA",jak,353,false);AddRow("Instalar en una carpeta nueva",destination,419,true);
  try{var drive=DriveInfo.GetDrives().Where(d=>d.IsReady&&d.DriveType==DriveType.Fixed).OrderByDescending(d=>d.AvailableFreeSpace).First();destination.Text=Path.Combine(Directory.Exists(@"F:\")?@"F:\":drive.RootDirectory.FullName,"RatchetJak-Beta47");}catch{destination.Text=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),"RatchetJak-Beta47");}
  generate.SetBounds(34,490,350,46);generate.Tag="Generar beta y EXE del escritorio";generate.BackColor=Color.FromArgb(227,106,34);generate.ForeColor=Color.Black;generate.FlatStyle=FlatStyle.Flat;generate.Click+=async(s,e)=>await StartBuild();Controls.Add(generate);
  status.SetBounds(405,490,490,60);status.Tag="No incluye los juegos. Campañas completas aún pendientes.";Controls.Add(status);
  progress.SetBounds(34,555,860,7);progress.Style=ProgressBarStyle.Marquee;progress.Visible=false;Controls.Add(progress);
  log.SetBounds(34,575,860,155);log.Multiline=true;log.ReadOnly=true;log.ScrollBars=ScrollBars.Vertical;log.BackColor=Color.FromArgb(8,14,23);log.ForeColor=Color.FromArgb(161,223,218);log.Font=new Font("Consolas",9F);Controls.Add(log);
  RefreshLanguage();
  FormClosing+=(s,e)=>{if(busy){e.Cancel=true;status.Text=Lang.T("La generación sigue activa. Espera a que termine; el registro muestra la fase actual.");}};
 }
 void AddRow(string title,TextBox box,int y,bool folder){
  Controls.Add(new Label{Left=34,Top=y,Width=810,Height=23,Tag=title,UseMnemonic=false});box.SetBounds(34,y+25,742,29);box.BackColor=Color.FromArgb(30,42,57);box.ForeColor=Color.White;Controls.Add(box);
  var button=new Button{Left=789,Top=y+24,Width=105,Height=31,Tag="Elegir…",FlatStyle=FlatStyle.Flat};
  button.Click+=(s,e)=>{if(busy)return;if(folder){using(var dialog=new FolderBrowserDialog{Description=Lang.T("Elige una carpeta vacía o nueva")})if(dialog.ShowDialog()==DialogResult.OK)box.Text=dialog.SelectedPath;}else{using(var dialog=new OpenFileDialog{Filter=Lang.T("ISO de PlayStation 2")+"|*.iso",CheckFileExists=true})if(dialog.ShowDialog()==DialogResult.OK)box.Text=dialog.FileName;}};Controls.Add(button);
 }
 void RefreshLanguage(){
  Text=Lang.T("Ratchet&Jak — Generador experimental");
  foreach(Control control in Controls)if(control.Tag is string)control.Text=Lang.T((string)control.Tag);
  summary.Text=Lang.T("BETA EXPERIMENTAL")+" · V19 alpha47\n"+Lang.T("Elige tus dos ISO. Se creará una instalación nueva y un EXE con este icono en tu escritorio.");
 }
 void Line(string value){if(IsDisposed)return;if(InvokeRequired){BeginInvoke((Action<string>)Line,value);return;}log.AppendText(value+Environment.NewLine);if(value.StartsWith("FASE:"))status.Text=value.Substring(5).Trim();}
 async Task StartBuild(){
  if(busy)return;busy=true;language.Enabled=false;generate.Enabled=false;progress.Visible=true;log.Clear();
  try{var c=new Request{RatchetIso=ratchet.Text,JakIso=jak.Text,Destination=destination.Text,Language=Lang.Code};await Task.Run(()=>Generator.Build(c,Line));status.Text=Lang.T("LISTO. Abre Ratchet&Jak desde tu escritorio.");}
  catch(Exception e){Line("ERROR: "+Lang.T(e.Message));status.Text=Lang.T("No completado. Lee el registro; la instalación anterior está a salvo.");}
  finally{busy=false;language.Enabled=true;generate.Enabled=true;progress.Visible=false;}
 }
}
