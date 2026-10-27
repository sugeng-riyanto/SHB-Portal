from django import template
from django.utils.translation import get_language

register = template.Library()
TEXT = {
'Selamat pagi':('Good morning','早安'),'Selamat siang':('Good afternoon','午安'),'Selamat sore':('Good afternoon','下午好'),'Selamat malam':('Good evening','晚安'),
'Beranda':('Home','首頁'),'Dashboard':('Dashboard','儀表板'),'Masuk':('Sign in','登入'),'Keluar':('Sign out','登出'),'Profil':('Profile','個人資料'),'Kabar sekolah':('School news','學校消息'),'Super Admin':('Super Admin','超級管理員'),'Integrasi':('Integrations','整合設定'),
'Selamat datang':('Welcome','歡迎'),'Masuk menggunakan akun sekolah Anda.':('Sign in with your school account.','請使用您的學校帳戶登入。'),'Tampilkan password':('Show password','顯示密碼'),'Sembunyikan password':('Hide password','隱藏密碼'),'Ubah password':('Change password','更改密碼'),'Simpan password':('Save password','儲存密碼'),'Profil saya':('My profile','我的個人資料'),'Simpan profil':('Save profile','儲存個人資料'),
'Jika ini login pertama, buat password baru sebelum melanjutkan.':('If this is your first sign-in, create a new password before continuing.','首次登入時，請先設定新密碼再繼續。'),
'PORTAL SEKOLAH':('SCHOOL PORTAL','學校入口網站'),'Ringkasan':('Overview','總覽'),'Bukti transfer':('Payment proof','付款證明'),'Pesan masuk':('Inbox','收件匣'),'Rekening sekolah':('School bank accounts','學校銀行帳戶'),'Kirim pesan':('Send message','傳送訊息'),'Status email':('Email status','電子郵件狀態'),'Impor XLSX':('Import XLSX','匯入 XLSX'),'Data murid':('Students','學生資料'),'DASHBOARD':('DASHBOARD','儀表板'),'Lihat informasi sesuai akses akun Anda.':('View information available to your account.','查看您的帳戶可存取的資訊。'),'Akses Anda':('Your access','您的存取權限'),'Belum ada peran yang ditugaskan. Hubungi admin sekolah.':('No role has been assigned. Please contact the school administrator.','尚未指派角色，請聯絡學校管理員。'),'Ringkasan pimpinan':('Leadership overview','管理概覽'),'tagihan aktif':('active bills','筆有效帳單'),'Nilai pokok Rp':('Total charges IDR','帳單總額印尼盾'),'Tagihan dalam lingkup akses':('Bills available to you','您可查看的帳單'),'Murid':('Student','學生'),'Kelas':('Class','班級'),'Tagihan':('Bill','帳單'),'Nominal':('Amount','金額'),'Jatuh tempo':('Due date','到期日'),'Bukti':('Proof','證明'),'Tidak ada data yang tersedia.':('No data available.','目前沒有資料。'),
'BERSAMA MENDUKUNG PERJALANAN ANAK':('SUPPORTING YOUR CHILD TOGETHER','攜手支持孩子成長'),'Terhubung dengan sekolah,':('Stay connected with school,','與學校保持聯繫，'),'lebih tenang setiap hari.':('with peace of mind.','每天更安心。'),'Bapak dan Ibu dapat mengikuti informasi pembayaran dan kabar sekolah di satu tempat, kapan pun dibutuhkan. Kami siap membantu jika ada hal yang ingin ditanyakan.':('Find payment information and school news in one place, whenever you need it. We are here to help if you have questions.','隨時在一處查看付款資訊與學校消息。如有疑問，我們樂意提供協助。'),'Masuk ke portal':('Sign in to the portal','登入入口網站'),'Lihat kabar sekolah':('View school news','查看學校消息'),'Gunakan akun yang telah disiapkan oleh sekolah untuk masuk.':('Sign in using the account provided by the school.','請使用學校提供的帳戶登入。'),'UNTUK BAPAK DAN IBU':('FOR PARENTS AND GUARDIANS','給家長與監護人'),'Informasi yang jelas, komunikasi yang dekat.':('Clear information, closer communication.','資訊清晰，溝通更貼近。'),'Informasi pembayaran':('Payment information','付款資訊'),'Mudah dipantau':('Easy to follow','輕鬆查看'),'Terhubung dengan sekolah':('Connected with school','與學校保持聯繫'),'Kami siap membantu':('We are here to help','我們樂意協助'),
}
@register.simple_tag
def tr(value):
    lang=(get_language() or 'en').lower()
    if lang.startswith('id'): return value
    pair=TEXT.get(value)
    if not pair: return value
    return pair[1] if lang.startswith('zh-hant') else pair[0]
