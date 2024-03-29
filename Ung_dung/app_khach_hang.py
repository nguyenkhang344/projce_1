from Ung_dung import app
from flask import  redirect, render_template , session, request, Markup
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
from sqlalchemy import update

from Ung_dung.Xu_ly.Khach_tham_quan.Xu_ly_3L import *

#***cấu hình mail********
from flask_mail import Mail, Message
mail=Mail(app)

#**********import form**************
    # import ckeditor
from Ung_dung.Xu_ly.Khach_tham_quan.Xu_ly_Form import*
from flask_ckeditor import CKEditor

#************khởi tạo session_1*****
Base.metadata.bind= engine
DBSession= sessionmaker(bind=engine)
session_1=DBSession()

@app.route('/', methods=['GET','POST'])
def index():
#**************Khởi động dữ liệu *********
    Danh_sach_SP_chon =[]
    Danh_sach_san_pham = Doc_danh_sach_SP()
    Da_dang_nhap = False
    Danh_sach_SP_hien_thi=Danh_sach_san_pham
    Chuoi_tra_cuu =""
#***************Menu lọc sản phẩm**********
    Danh_sach_loai_SP= Doc_danh_sach_loai_SP()
    Chuoi_HTML_Menu = Tao_chuoi_HTML_Menu(Danh_sach_loai_SP)
    

#**************Chức năng tìm kiếm********
    if request.form.get('Th_Chuoi_tra_cuu')!=None:
        Chuoi_tra_cuu=request.form.get('Th_Chuoi_tra_cuu')
        print('Chuỗi tra cứu',Chuoi_tra_cuu)
        Danh_sach_SP_hien_thi =Tra_cuu_SP(Chuoi_tra_cuu,Danh_sach_san_pham)

#**************Menu khach hang************

    Chuoi_HTML_Khach_hang = ""
    Chuoi_QL_Dang_nhap =""
    if session.get('Khach_hang_dang_nhap'):
        print('get sessions')
        Khach_hang_dang_nhap = session['Khach_hang_dang_nhap']
        Chuoi_HTML_Khach_hang= Tao_chuoi_HTML_Khach_hang(Khach_hang_dang_nhap)

        #*xử lý button"thêm vào giỏ hàng
        Da_dang_nhap=True
    else:
        Chuoi_QL_Dang_nhap = '''
        <li>
        <a href="/Dang_nhap_khach_hang">
        <button class="btn button3" role="button">Đăng nhập</button></a>
        </li>
        <li>
        <a href="/Dang_ky">
        <button class="btn button4" role="button">Đăng ký</button></a>
        </li>
        '''


#*************Khởi tạo giỏ hàng***********
    if request.method == 'POST':
        print("đã nhận post")
        if request.form.get('Th_Ma_so')!=None:
         #Truy vấn session['Gio_hang] khi khách chọn sản phẩm tiếp theo
                if session.get('Gio_hang'):
                       Danh_sach_SP_chon = session['Gio_hang']['Gio_hang']
                ma_so=request.form.get('Th_Ma_so')
                so_luong = request.form.get('Th_So_luong')

                #********xử lý update số lượng khi khách hàng chọn lại sản phẩm đã có trong giỏ hàng*******
                #Lưu ý : đang xử lý với 1 SP thông  qua mã số
                #Check đã có tivi trong giõ hàng chưa :
                # =>tra cứu mã số đang xử lý có trong Danh_sach_SP_chon(Lay_chi_tiet_SP không rỗng)
                # => San phẩm đã có trong giõ hàng 
                if Lay_chi_tiet_SP(Danh_sach_SP_chon,ma_so)!=None:
                    SP_chon_cu = Lay_chi_tiet_SP(Danh_sach_SP_chon,ma_so)
                        # Lấy số lượng đã có trong giỏ hàng bằng so_luong_cu
                    so_luong_cu =SP_chon_cu["So_luong"]
                        # lưu ý so_luong mới được lấy khi người dùng click chọn lại sản phẩm
                        # bằng hàm SP_chon["So_luong"] = so_luong bên dưới
                        # update lại số lượng mới
                    print ("số lượng cũ",so_luong_cu)
                    so_luong= int(so_luong_cu) + int(so_luong)
                        #so_luong đã dược update phải remove Tivi_cu 
                        # để phiên update sau so_luong nay thành so_luong cũ 
                        #Lưu ý: SP_chon không bị mất khỏi giỏ hàng sau khi remove vì
                        #hàm Danh_sach_SP_chon.append(SP_chon) bên dưới đã update lại SP
                    Danh_sach_SP_chon.remove(SP_chon_cu)

                # setup so_luong
                SP_chon = Lay_chi_tiet_SP(Danh_sach_san_pham,ma_so)
                SP_chon["So_luong"] = so_luong
                Danh_sach_SP_chon.append(SP_chon)
                print("Danh sách_sản phẩm_chọn", Danh_sach_SP_chon)
                session['Gio_hang']={'Gio_hang':Danh_sach_SP_chon}

    #***************cập nhật giỏ hàng *************
    if request.form.get('Th_Ma_so_1')!=None:
         #Truy vấn session['Gio_hang] khi khách chọn sản phẩm tiếp theo
        Danh_sach_SP_chon_update=[]

        # truyền dữ liệu vào Danh_sach_SP_chon_update để hiện thị giỏ hàng
        if session.get('Gio_hang'):
            Danh_sach_SP_chon_update = session['Gio_hang']['Gio_hang']

        ma_so_1=request.form.get('Th_Ma_so_1')
        print("mã số 1",ma_so_1)
        so_luong_1 = int(request.form.get('Th_So_luong_1'))
        SP_chon = Lay_chi_tiet_SP(Danh_sach_SP_chon_update,ma_so_1)
            
            # trường hợp số lượng =0 và sp_chon vẫn còn => tiến hành xóa sp
        if SP_chon !=None:
            Danh_sach_SP_chon_update.remove(SP_chon)
        if so_luong_1 >0 and SP_chon!=None:
            #cập nhật số lượng
            SP_chon['So_luong'] =so_luong_1
            Danh_sach_SP_chon_update.append(SP_chon)
        session['Gio_hang']={'Gio_hang':Danh_sach_SP_chon_update}
        if session.get('Gio_hang'):
            Danh_sach_SP_chon = session['Gio_hang']['Gio_hang']
    if session.get('Gio_hang'):
        Danh_sach_SP_chon = session['Gio_hang']['Gio_hang']

    #****************kết xuất dữ liệu****************
    chuoi_HTML_gio_hang = Tao_chuoi_HTML_gio_hang(Danh_sach_SP_chon)
    chuoi_the_hien=Tao_chuoi_HTML_Danh_sach_SP(Danh_sach_SP_hien_thi)
    chuoi_modal = Tao_chuoi_HTML_Modal(Danh_sach_san_pham,Da_dang_nhap)
    Khung =render_template("khach_hang/MH_Khach_hang.html",
        Chuoi_HTML_Menu=Chuoi_HTML_Menu,
        Chuoi_tra_cuu= Chuoi_tra_cuu,
        Chuoi_HTML_Khach_hang= Chuoi_HTML_Khach_hang,
        Chuoi_QL_Dang_nhap=Markup(Chuoi_QL_Dang_nhap),
        chuoi_HTML_gio_hang=chuoi_HTML_gio_hang,
        chuoi_the_hien=chuoi_the_hien,chuoi_modal=chuoi_modal)
    return Khung

@app.route('/Dang_ky', methods=['GET','POST'])
def Dang_ky():
    Chuoi_ket_qua=""
    form = Form_Khach_hang()
    if form.validate_on_submit():
        ma_khach_hang=request.form['Th_Ma_so']
        ten_khach_hang = request.form['Th_Ho_ten']
        phai=request.form['Th_Phai']
        ngay_sinh = request.form['Th_Ngay_sinh']
        dia_chi = request.form['Th_Dia_chi']
        dien_thoai=request.form['Th_Dien_thoai']
        email = request.form['Th_Email']
        mat_khau = request.form['Th_Mat_khau']
        
        kh= KhachHang(ma_khach_hang=ma_khach_hang, ten_khach_hang=ten_khach_hang, phai=phai, ngay_sinh=ngay_sinh,
                        dia_chi=dia_chi, dien_thoai=dien_thoai,email=email,matkhau=mat_khau)
        print(kh)
        session_1.add(kh)
        try:
            session_1.commit()
            Chuoi_ket_qua = '''
            
                <div class="row">
                    <div class="col-lg-6 col-sm-6 " style="visibility: visible;">
                        <div class="work_bottom"> <span>Đã tạo tài khoản thành công</span> 
                        <a href="/" class="contact_btn">Trở lại trang chủ</a> 
                    </div>
                </div>
 
            '''
        except exc.SQLAlchemyError: 
            print(exc.SQLAlchemyError)
            Chuoi_ket_qua= '''
        
                <div class="row" style="margin-top:1px;">
                    <div class="col-lg-6 col-sm-6 " style="visibility: visible;">
                        <div class="work_bottom"> <span>Tên đăng nhập này đã có, Vui lòng chọn tên đăng nhập khác</span> 
                    </div>
                </div>
      
            '''
    return render_template('khach_hang/MH_Dang_ky.html',form=form, Chuoi_ket_qua=Markup(Chuoi_ket_qua))

@app.route("/Dang_nhap_khach_hang", methods=['GET','POST'])
def Dang_nhap():
#*****Khởi động dữ liệu nguồn/nội bộ*******
    if session.get('Khach_hang_dang_nhap'):
        return redirect(url_for('index'))
    Danh_sach_khach_hang=Doc_danh_sach_Khach_hang()
    Ten_dang_nhap=""
    Mat_khau=""
    Chuoi_Thong_bao= "Xin vui lòng Nhập Tên đăng nhập và Mật khẩu"
    if request.method=='POST':
        Ten_dang_nhap=request.form.get('Th_Ten_dang_nhap')
        Mat_khau= request.form.get('Th_Mat_khau')
        Khach_hang= Dang_nhap_Khach_hang(Danh_sach_khach_hang,Ten_dang_nhap,Mat_khau)
        print("khách hàng",Khach_hang)
        Hop_le=(Khach_hang!=None)
        if Hop_le:
            session['Khach_hang_dang_nhap']=Khach_hang
            return redirect(url_for('index'))
        else:
            Chuoi_Thong_bao="Đăng nhập không hợp lệ"
    Khung =render_template('khach_hang/MH_Dang_nhap.html',Chuoi_Thong_bao=Chuoi_Thong_bao)
    return Khung

@app.route("/Dang_xuat_khach_hang")
def Dang_xuat_khach_hang():
    session.pop('Khach_hang_dang_nhap',None)
    return redirect(url_for("index"))
@app.route('/Dat_hang',methods=['GET','POST'])
def Dat_hang():
    Chuoi_QL_Dang_nhap =""
    Chuoi_HTML_dat_hang =""
    Chuoi_Thong_bao =""
    if session.get('Khach_hang_dang_nhap'):
        if session.get('Gio_hang'):
            SP_dat_hang = session['Gio_hang']['Gio_hang']
            Khach_hang_dang_nhap = session['Khach_hang_dang_nhap']
            Chuoi_HTML_dat_hang= Tao_chuoi_HTML_Dat_hang(SP_dat_hang,Khach_hang_dang_nhap)
            Chuoi_HTML_Khach_hang= Tao_chuoi_HTML_Khach_hang(Khach_hang_dang_nhap)

            if request.method =='POST':
                for san_pham in SP_dat_hang:
                    so_luong_ton =san_pham['so_luong_ton']
                    so_luong = int(san_pham["So_luong"])
                    ma_san_pham =san_pham["ma_san_pham"]
                    so_luong_ton_update = so_luong_ton-so_luong
                    session_1.query(San_pham).filter(San_pham.ma_san_pham== ma_san_pham).update({"so_luong_ton":so_luong_ton_update})
                    session_1.commit()



                ngay_hd = datetime.now()
                ma_khach_hang = session['Khach_hang_dang_nhap']['ma_khach_hang']
                tri_gia = request.form.get('Th_Tong_tien')
                so_hoa_don =request.form.get('Th_So_hoa_don')
                print("trị giá",tri_gia)
                print("mã khách hàng",ma_khach_hang)
                print("số hóa đơn",so_hoa_don)
                print("ngày HD",ngay_hd)
                hd= HoaDon( ngay_hd=str(ngay_hd), ma_khach_hang=ma_khach_hang, tri_gia=tri_gia)
                session_1.add(hd)
                try:
                    session_1.commit()
                    return redirect(url_for('Ket_qua_dat_hang'))
                except exc.SQLAlchemyError: 
                    print("lỗi sql",exc.SQLAlchemyError)
                    pass
        else:
            return redirect(url_for("index"))
    else:
        Chuoi_QL_Dang_nhap = '''
        <a href="/Dang_nhap_khach_hang">
        <button class="btn button3" role="button">Đăng nhập</button></a>
        '''
    Khung= render_template("khach_hang/MH_Dat_hang.html",
                        Chuoi_HTML_Khach_hang= Chuoi_HTML_Khach_hang,
                        Chuoi_QL_Dang_nhap=Chuoi_QL_Dang_nhap,
                        Chuoi_HTML_dat_hang=Chuoi_HTML_dat_hang)
    return Khung

@app.route("/Dat_hang_ket_qua")
def Ket_qua_dat_hang():
    Ngay=datetime.now().strftime('%d-%m-%Y')
    Khach_hang = session['Khach_hang_dang_nhap']
    San_pham_dat_hang =session['Gio_hang']['Gio_hang']

    Tieu_de="Xác nhận đặt hàng - Shop Mỹ phẩm đẹp -" +Ngay
    Noi_dung_mail="Thân gửi khách hàng :" + Khach_hang['ten_khach_hang']+\
        "<br/>Đơn hàng của bạn ở Shop Mỹ phẩm Đẹp đã được đặt thành công"+\
        "<br/>Chi tiết đơn hàng:"
    Tong_tien=0
    for san_pham in San_pham_dat_hang:
        CT_ID_SP = san_pham['ma_san_pham']
        CT_So_luong= san_pham['So_luong']
        CT_don_gia =int(san_pham['don_gia'] )* int(san_pham['So_luong'])
        #lấy số hóa đơn mới được update
        A_So_hoa_don = session_1.query(HoaDon).order_by(HoaDon.so_hoa_don.desc()).first()
        So_HD= A_So_hoa_don.so_hoa_don
        print("đơn giá",CT_don_gia)

        #update CT hóa đơn
        Chi_tiet_Hoa_don = CtHoaDon(id_san_pham=CT_ID_SP,so_luong=CT_So_luong,don_gia=CT_don_gia,so_hoa_don=So_HD)
        session_1.add(Chi_tiet_Hoa_don)
        session_1.commit()
        #Tạo mail chi tiết đơn hàng
        Tong_tien+= CT_don_gia
        Noi_dung_mail+= "<br/>"+san_pham['ten_san_pham']+"---Số lượng:"+str(san_pham['So_luong'])+"---Thành tiền:{:,}".format(CT_don_gia).replace(",",".")
        
    Noi_dung_mail+= "<br/>Tổng tiền :{:,}".format(Tong_tien).replace(",",".") +\
                    "<br/>Cảm ơn quý khách đã ủng hộ shop, sản phẩm sẽ được giao đến địa chỉ :"+ Khach_hang['dia_chi']

    msg=Message(Tieu_de,sender='python244t7cn@gmail.com', recipients=[Khach_hang['email']])
    mail.body=Noi_dung_mail
    msg.html= mail.body
    mail.send(msg)

    session.pop('Gio_hang',None)
    return render_template('khach_hang/MH_Dat_hang_thanh_cong.html')