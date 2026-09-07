using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;

var failures = 0;
foreach (var path in args)
{
    using var document = SpreadsheetDocument.Open(path, false);
    var validator = new OpenXmlValidator(FileFormatVersions.Office2019);
    var errors = validator.Validate(document).ToList();
    Console.WriteLine($"{Path.GetFileName(path)}: {errors.Count} Open XML errors");
    foreach (var error in errors.Take(80))
        Console.WriteLine($"{error.Id}: {error.Description}\n  {error.Part?.Uri} {error.Path?.XPath}");
    failures += errors.Count;
}
if (args.Length == 0) throw new ArgumentException("Workbook paths are required");
return failures == 0 ? 0 : 1;
