# Matriks peran SHB Portal

| Fitur | Admin sekolah | Kepala sekolah | Yayasan | Wali kelas | Orang tua/wali |
|---|---|---|---|---|---|
| Dashboard dan alert jatuh tempo | Detail sesuai scope | Agregat sesuai scope | Agregat sesuai scope | Kelas ditugaskan | Anak terhubung |
| XLSX dan filter | Impor/ekspor sesuai izin; preview dan audit | Filter laporan sesuai scope | Filter agregat | Filter kelas sendiri | Pilih anak dan tagihan |
| Murid, relasi wali, undangan | Kelola dan undang sesuai scope | Laporan dan akses sesuai izin | Agregat | Lihat murid kelas | Lihat anak terhubung |
| Tagihan dan pembayaran | Kelola, verifikasi/koreksi dengan audit | Agregat; bukti individual dalam scope | Agregat | Status kelas; detail sesuai kebijakan | Tagihan dan histori anak |
| Bukti transfer | Preview dan verifikasi dalam scope | Preview foto dan nominal dalam scope | Tidak ada akses individual default | Preview foto dan nominal murid kelas ditugaskan | Buat, lihat, ubah/tarik milik sendiri sebelum verifikasi |
| Rekening bank sekolah | Pilih rekening aktif di tagihan sesuai izin | CRUD sesuai scope; arsip jika dipakai | Tidak | Tidak | Lihat tujuan di tagihan anak |
| Kirim pesan | Semua/per kelas/individu/custom; portal, email dan WhatsApp resmi | Baca pengumuman dan laporan | Baca pengumuman dan laporan | Terima sesuai sasaran | Inbox dan notifikasi pribadi |
| Pengumuman | Kelola | Baca atau kelola jika diotorisasi | Baca sesuai sasaran | Baca sesuai sasaran | Baca sesuai sasaran |
| WhatsApp bantuan | Tombol chat | Tombol chat | Tombol chat | Tombol chat | Tombol chat |

Semua operasi ditegakkan server-side, termasuk file privat, ekspor dan API. Hubungan wali-murid diverifikasi; kepala sekolah dan wali kelas mendapat hak eksplisit melihat bukti transfer individual dalam scope sesuai permintaan. Aksi frontend dalam preview bukan bukti keamanan. Foto bukti tidak otomatis membuktikan pembayaran; hanya admin berwenang memverifikasi. Setiap peran punya profil, logout, bahasa dan tema.

**Pengaturan sekolah:** admin sesuai scope mengelola logo, nomor WhatsApp bantuan dan jadwal alert; kepala sekolah dapat melihat atau mengubah bila diberi hak khusus. Pengguna lain melihat logo dan tombol bantuan sesuai konfigurasi, tanpa hak mengubahnya.
