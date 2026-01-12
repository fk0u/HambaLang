# HambaLang v2.0 - Syntax Cheat Sheet

## Quick Reference

### Comments
```hl
// Single-line comment
```

### Print / Output
```hl
lapor "Message"      // Indonesian style
print "Message"      // Universal style
```

### Variables
```hl
nama = "Value"
angka = 123
aktif = benar        // true
nonaktif = salah     // false
kosong_var = kosong  // null
```

### Data Types

**String:**
```hl
text = "Hello"
text2 = 'World'
gabung = text + " " + text2
```

**Number:**
```hl
integer = 42
float_num = 3.14
```

**Boolean:**
```hl
ya = benar
tidak = salah
```

**Array:**
```hl
list = [1, 2, 3, 4, 5]
mixed = ["text", 123, benar]
item = list[0]
list[1] = 99
```

**Object:**
```hl
obj = {"key": "value", "num": 123}
val = obj["key"]
obj["new"] = "data"
```

### Operators

**Arithmetic:**
```hl
+ - * / %
```

**Comparison:**
```hl
== != < > <= >=
```

**Logical:**
```hl
dan     // and
atau    // or
```

### Control Flow

**If/Elif/Else:**
```hl
jika condition
    // code
ataujika other_condition
    // code
atau
    // code
akhir
```

**While Loop:**
```hl
selama condition
    // code
    hentikan    // break
    lanjut      // continue
akhir
```

**For Loop (Range):**
```hl
untuk i dari 1 sampai 10
    lapor teks(i)
akhir
```

**For Loop (Array):**
```hl
untuk item dalam array
    lapor item
akhir
```

### Functions

**Definition:**
```hl
fungsi namaFungsi(param1, param2)
    hasil = param1 + param2
    kembalikan hasil
akhir
```

**Call:**
```hl
result = namaFungsi(10, 20)
```

### Built-in Functions

```hl
panjang(x)              // length
tipe(x)                 // type
angka(x)                // to number
teks(x)                 // to string
tambahArray(arr, val)   // append
hapusArray(arr, index)  // remove
```

### Database

```hl
sambungDB("db", "sqlite", "file.db")
hasil = queryDB("db", "SELECT * FROM table")
tutupDB("db")
```

### File I/O

```hl
tulisFile("file.txt", "content")
content = bacaFile("file.txt")
```

### HTTP

```hl
resp = httpGet("url")
resp = httpPost("url", {"key": "val"})
```

### Satire Functions

```hl
Mangkrak(1000)      // Delay + events
Korupsi(25)         // Reduce budget 25%
RapatInfinite()     // Infinite loop
selesai()           // Terminate
```

### Built-in Variables

```hl
anggaran            // Budget (1000000000)
status_proyek       // Project status
progress            // Progress (0-100)
```

### Example Program

```hl
// Calculator
fungsi kalkulator(a, b, op)
    jika op == "+"
        kembalikan a + b
    ataujika op == "-"
        kembalikan a - b
    ataujika op == "*"
        kembalikan a * b
    ataujika op == "/"
        kembalikan a / b
    akhir
akhir

hasil = kalkulator(10, 5, "+")
lapor "Hasil: " + teks(hasil)

// Loop
untuk i dari 1 sampai 5
    lapor "Angka: " + teks(i)
akhir

// Satire
Korupsi(20)
selesai()
```

---

**Full documentation:** `docs/index.html`
