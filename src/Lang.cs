using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
internal static class Lang {
 internal static readonly string[] Codes={"en","fr","de","es","it"};
 internal static readonly string[] Names={"English","Français","Deutsch","Español","Italiano"};
 internal static string Code=DefaultCode();
 static readonly Dictionary<string,object> Catalog=Read();
 static string DefaultCode(){string code=CultureInfo.CurrentUICulture.TwoLetterISOLanguageName;return Array.IndexOf(Codes,code)>=0?code:"en";}
 static Dictionary<string,object> Read(){using(var s=Assembly.GetExecutingAssembly().GetManifestResourceStream("locales.json"))using(var r=new StreamReader(s))return DiscSafety.Json.Deserialize<Dictionary<string,object>>(r.ReadToEnd());}
 internal static void Select(string code){if(String.IsNullOrWhiteSpace(code))return;if(Array.IndexOf(Codes,code)<0)throw new IOException("Unsupported language: "+code);Code=code;}
 internal static string T(string source){
  var table=(Dictionary<string,object>)Catalog["setup"];object row;
  if(table.TryGetValue(source,out row))return ((Dictionary<string,object>)row)[Code].ToString();
  // A diagnostic may append a path, serial or number to a translated prefix.
  foreach(var item in table)if(item.Key.EndsWith(": ")&&source.StartsWith(item.Key,StringComparison.Ordinal))return ((Dictionary<string,object>)item.Value)[Code]+source.Substring(item.Key.Length);
  return source;
 }
}
