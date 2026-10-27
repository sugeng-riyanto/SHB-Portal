# Template email informasi pembayaran bilingual

## Bahasa Indonesia
**Subjek:** Informasi Pembayaran Sekolah — Sekolah Harapan Bangsa

Yth. Bapak/Ibu {{ guardian_name }},

Semoga Bapak/Ibu dan keluarga dalam keadaan baik. Dengan hormat, kami ingin menyampaikan informasi pembayaran sekolah untuk putra/putri Bapak/Ibu:

- Nama murid: {{ student_name }}
- Kelas: {{ class_name }}
- Jenis / periode tagihan: {{ bill_type }} / {{ period }}
- Jatuh tempo: {{ due_date }}
- Sisa yang perlu dibayar: {{ amount_due }}

Rincian tagihan, termasuk denda apabila ada, serta petunjuk pembayaran dapat Bapak/Ibu lihat melalui portal sekolah: {{ portal_url }}.

Apabila pembayaran telah dilakukan, Bapak/Ibu dapat mengunggah bukti melalui portal. Status akan diperbarui setelah diperiksa oleh administrasi. Jika ada pertanyaan, kesulitan, atau informasi yang perlu dikoreksi, kami dengan senang hati membantu melalui {{ school_contact }}.

Terima kasih atas perhatian, dukungan, dan kerja sama Bapak/Ibu. Kami sangat menghargainya.

Hormat kami,  
Tim Administrasi  
Sekolah Harapan Bangsa

## English
**Subject:** School Payment Information — Sekolah Harapan Bangsa

Dear {{ guardian_name }},

We hope you and your family are doing well. We are writing to share the following school payment information for your child:

- Student: {{ student_name }}
- Class: {{ class_name }}
- Charge / period: {{ bill_type }} / {{ period }}
- Due date: {{ due_date }}
- Outstanding balance: {{ amount_due }}

You can find the full details, including any applicable late fee, and payment instructions in the school portal: {{ portal_url }}.

If you have already made the payment, you may upload your proof of payment through the portal. The status will be updated once our administration team has reviewed it. If you have any questions, need assistance, or notice information that should be corrected, please contact us at {{ school_contact }}. We will be happy to help.

Thank you very much for your attention, support, and cooperation. We truly appreciate it.

Kind regards,  
Administration Team  
Sekolah Harapan Bangsa

## Implementasi
Versi HTML ada pada `portal/templates/email/payment_id.html` dan `payment_en.html`. Font Arial/Helvetica/sans-serif, warna biru tua, hijau, merah dan abu-abu, dengan CSS inline untuk kompatibilitas email. Variabel harus berasal dari data terverifikasi, autoescape HTML aktif dan tautan berasal dari domain resmi yang sudah dikonfigurasi, bukan input penerima. Kirim individual sesuai preferensi bahasa, tanpa CC massal; preview isi dan penerima sebelum pengiriman. HTML dan teks biasa perlu dikirim sebagai multipart/alternative saat layanan email diimplementasikan. Templat ini belum terhubung SMTP atau pengiriman massal.
