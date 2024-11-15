import decimal
import sqlite3
import re
from tkinter import messagebox
from PIL import Image
from customtkinter import *

print("""
 $$$$$$\    $$\                          $$\     $$\                            $$$$$$\                      $$\ $$\                     $$\     $$\                     
$$  __$$\   $$ |                         $$ |    \__|                          $$  __$$\                     $$ |\__|                    $$ |    \__|                    
$$ /  \__|$$$$$$\    $$$$$$\   $$$$$$\ $$$$$$\   $$\ $$$$$$$\   $$$$$$\        $$ /  $$ | $$$$$$\   $$$$$$\  $$ |$$\  $$$$$$$\ $$$$$$\ $$$$$$\   $$\  $$$$$$\  $$$$$$$\  
\$$$$$$\  \_$$  _|   \____$$\ $$  __$$\\_$$  _|  $$ |$$  __$$\ $$  __$$\       $$$$$$$$ |$$  __$$\ $$  __$$\ $$ |$$ |$$  _____|\____$$\\_$$  _|  $$ |$$  __$$\ $$  __$$\ 
 \____$$\   $$ |     $$$$$$$ |$$ |  \__| $$ |    $$ |$$ |  $$ |$$ /  $$ |      $$  __$$ |$$ /  $$ |$$ /  $$ |$$ |$$ |$$ /      $$$$$$$ | $$ |    $$ |$$ /  $$ |$$ |  $$ |
$$\   $$ |  $$ |$$\ $$  __$$ |$$ |       $$ |$$\ $$ |$$ |  $$ |$$ |  $$ |      $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |$$ |$$ |     $$  __$$ | $$ |$$\ $$ |$$ |  $$ |$$ |  $$ |
\$$$$$$  |  \$$$$  |\$$$$$$$ |$$ |       \$$$$  |$$ |$$ |  $$ |\$$$$$$$ |      $$ |  $$ |$$$$$$$  |$$$$$$$  |$$ |$$ |\$$$$$$$\\$$$$$$$ | \$$$$  |$$ |\$$$$$$  |$$ |  $$ |
 \______/    \____/  \_______|\__|        \____/ \__|\__|  \__| \____$$ |      \__|  \__|$$  ____/ $$  ____/ \__|\__| \_______|\_______|  \____/ \__| \______/ \__|  \__|
                                                               $$\   $$ |                $$ |      $$ |                                                                  
                                                               \$$$$$$  |                $$ |      $$ |                                                                  
                                                                \______/                 \__|      \__|                                                                                                                       
""")

app = CTk()
app.geometry("500x400")
set_appearance_mode("dark")
set_default_color_theme("dark-blue")
app.title("Dhaka Stock Exchange")
frame = CTkFrame(master=app)
img_label = CTkLabel(master=app)
wallet_frame = CTkFrame(master=app)
port = CTkFrame(master=app)
stock_frame = CTkFrame(master=app)


def connect_to_database():
    try:
        conn = sqlite3.connect('stock_market.db')
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        sys.exit()


connection = connect_to_database()
cursor = connection.cursor()


def get_wallet_balance(user_id):
    cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return decimal.Decimal(result[0]) if result else None


def update_wallet_balance(user_id, new_balance):
    sql = "UPDATE wallets SET balance = ? WHERE user_id = ?"
    cursor.execute(sql, (str(new_balance), user_id))
    connection.commit()


def refresh_balance(userid):
    global wallet_frame, amt
    balance = get_wallet_balance(userid)

    if balance >= 1000000:
        display = str(round(balance / 1000000, 2)) + " M"
    elif balance >= 1000:
        display = str(round(balance / 1000, 2)) + " K"
    else:
        display = str(balance)

    amt.configure(text=display)


def add_money_to_wallet(user_id, amount):
    current_balance = get_wallet_balance(user_id)
    if current_balance is not None:
        try:
            amount_decimal = decimal.Decimal(amount)
            new_balance = current_balance + amount_decimal
            update_wallet_balance(user_id, new_balance)
            messagebox.showinfo("Success", f"Added ৳{amount_decimal} to your wallet. New balance: ৳{new_balance}")
            refresh_balance(user_id)
        except decimal.InvalidOperation:
            messagebox.showerror("Error", "Please enter a valid number")
    else:
        messagebox.showerror("Error", "User wallet not found. Please check the user ID.")


def add(userid):
    new_bal = CTkInputDialog(text="Enter Amount To Add", title="Balance").get_input()
    if new_bal is not None and new_bal.strip() != "":
        add_money_to_wallet(userid, new_bal)
    else:
        messagebox.showerror("Error", "Please enter a valid amount")


def check_shares(user_id):
    sql = """SELECT c.company_name, s.shares_owned 
             FROM shares s 
             JOIN companies c ON s.company_id = c.company_id 
             WHERE user_id = ?"""
    cursor.execute(sql, (user_id,))
    results = cursor.fetchall()
    storage = {"WALTON": "WALTON", "Grameenphone Ltd": "GP", "ACI Limited": "ACI", "DUTCHBANGLA Bank": "DBBL",
               "LankaBangla Finance": "LANKABANGLA"}

    if results:
        data = {}
        for company, shares in results:
            data[storage[company]] = shares
        return data
    else:
        return {}


def update_user_shares(user_id, company_id, new_share_count):
    sql = "UPDATE shares SET shares_owned = ? WHERE user_id = ? AND company_id = ?"
    cursor.execute(sql, (new_share_count, user_id, company_id))
    connection.commit()


def get_stock_price(company_id):
    sql = "SELECT stock_price FROM companies WHERE company_id = ?"
    cursor.execute(sql, (company_id,))
    result = cursor.fetchone()
    return result[0] if result else 0.0


def add_shares_to_portfolio(user_id, company_id, shares):
    sql = "INSERT INTO shares (user_id, company_id, shares_owned) VALUES (?, ?, ?)"
    cursor.execute(sql, (user_id, company_id, shares))
    connection.commit()


def get_user_shares(user_id, company_id):
    sql = "SELECT shares_owned FROM shares WHERE user_id = ? AND company_id = ?"
    cursor.execute(sql, (user_id, company_id))
    result = cursor.fetchone()
    return result[0] if result else 0


def buy_shares(user_id, company):
    global wallet_frame
    global port
    global stock_frame
    ids = {"WALTON": "1", "GP": "2", "ACI": "3", "DBBL": "4", "LANKABANGLA": "5"}
    company_id = ids[company]
    shares_to_buy = CTkInputDialog(text="Enter Number of Shares To Buy", title=company).get_input()
    if shares_to_buy:
        shares_to_buy = int(shares_to_buy)
    else:
        return

    stock_price = get_stock_price(company_id)
    purchase_amount = shares_to_buy * float(stock_price)
    wallet_balance = float(get_wallet_balance(user_id))

    current_shares = get_user_shares(user_id, company_id)

    if wallet_balance >= purchase_amount:
        new_balance = wallet_balance - purchase_amount
        update_wallet_balance(user_id, new_balance)

        if current_shares > 0:
            # The user already owns shares in this company; update the share count.
            new_shares = current_shares + shares_to_buy
            update_user_shares(user_id, company_id, new_shares)
        else:
            # The user does not own shares in this company; insert a new entry.
            add_shares_to_portfolio(user_id, company_id, shares_to_buy)

        messagebox.showinfo("Done", f"{company} Shares Bought Successfully")
        wallet_frame.destroy()
        port.destroy()
        stock_frame.destroy()
        logged_in(user_id)

    else:
        messagebox.showerror("Error", "Insufficient balance to make the purchase.")


def remove_shares_from_portfolio(user_id, company_id, shares):
    current_shares = get_user_shares(user_id, company_id)

    if current_shares >= shares:
        new_share_count = current_shares - shares
        update_user_shares(user_id, company_id, new_share_count)
    else:
        print("You do not have enough shares to make the sale.")


def sell_shares(user_id, company):
    global stock_frame
    global port
    global wallet_frame
    ids = {"WALTON": "1", "GP": "2", "ACI": "3", "DBBL": "4", "LANKABANGLA": "5"}
    company_id = ids[company]
    shares_to_sell = CTkInputDialog(text="Enter Number of Shares To Sell", title=company).get_input()

    if shares_to_sell:
        shares_to_sell = int(shares_to_sell)
    else:
        return

    user_shares = int(get_user_shares(user_id, company_id))
    if user_shares >= shares_to_sell:
        stock_price = float(get_stock_price(company_id))
        sale_amount = shares_to_sell * stock_price
        wallet_balance = float(get_wallet_balance(user_id))
        new_balance = wallet_balance + sale_amount  # Update wallet balance with the sale amount
        update_wallet_balance(user_id, new_balance)  # Update the wallet balance in the database
        remove_shares_from_portfolio(user_id, company_id, shares_to_sell)
        messagebox.showinfo("Done", f"You have sold {shares_to_sell} shares of {company}.")
        wallet_frame.destroy()
        port.destroy()
        stock_frame.destroy()
        logged_in(user_id)
    else:
        messagebox.showerror("Error", "You do not have enough shares to make the sale.")


def out():
    global wallet_frame
    global port
    global stock_frame
    global top
    try:
        top.destroy()
    except:
        pass

    wallet_frame.destroy()
    port.destroy()
    stock_frame.destroy()

    page1()


def view(user_id, company):
    global top
    try:
        top.destroy()
    except:
        pass
    top = CTkToplevel(app)
    top.geometry("300x300")
    top.title(company)
    comp = CTkImage(Image.open(f"./images/{company}.png"), size=(200, 200))
    comp_l = CTkLabel(master=top, text="", image=comp)
    comp_l.pack()
    ids = {"WALTON": "1", "GP": "2", "ACI": "3", "DBBL": "4", "LANKABANGLA": "5"}

    price = get_stock_price(ids[company])
    price_label = CTkLabel(master=top, text=f"৳ {price}", font=("Roboto", 16))
    price_label.pack()
    buy_button = CTkButton(master=top, text="Buy", width=120, height=40, fg_color="#40e0d0", hover_color="#32cd32",
                           font=("Roboto", 24),
                           command=lambda: buy_shares(user_id, company))
    buy_button.place(x=20, y=250)

    sell_button = CTkButton(master=top, text="Sell", width=120, height=40, fg_color="#40e0d0", hover_color="#e2062c",
                            font=("Roboto", 24),
                            command=lambda: sell_shares(user_id, company))
    sell_button.place(x=160, y=250)


def logged_in(userid):
    global frame, img_label, wallet_frame, port, stock_frame, amt
    frame.destroy()
    img_label.destroy()
    balance = get_wallet_balance(userid)
    wallet_frame = CTkFrame(master=app, width=220, height=50)
    wallet_frame.grid(row=0, column=0, padx=10, pady=10)

    bal = CTkLabel(master=wallet_frame, text="Balance: ৳", font=("Roboto", 15))
    bal.place(x=20, y=10)

    if balance >= 1000000:
        display = str(round(balance / 1000000, 2)) + " M"
    elif balance >= 1000:
        display = str(round(balance / 1000, 2)) + " K"
    else:
        display = str(balance)

    amt = CTkLabel(master=wallet_frame, text=display, font=("Roboto", 15))
    amt.place(x=90, y=10)
    btn = CTkButton(master=wallet_frame, text="Add +", fg_color="#40e0d0", hover_color="#00ff00", width=60, height=20,
                    command=lambda: add(userid))
    btn.place(x=150, y=13)

    port = CTkFrame(master=app, width=220, height=320)
    port.grid(row=1, column=0, padx=10, pady=(0, 10))
    txt = CTkLabel(master=port, text="Portfolio", font=("Roboto", 24))
    txt.place(x=60, y=5)
    shares_data = check_shares(userid)
    for i, share in enumerate(shares_data):
        suitcase = CTkImage(dark_image=Image.open("./images/bagw.png"), light_image=Image.open("./images/bagb.png"),
                            size=(20, 15))
        bag = CTkLabel(master=port, text="", image=suitcase)
        bag.place(x=8, y=58 + 40 * i)
        stock_label = CTkLabel(master=port, text=f"{share} : {shares_data[share]} shares", font=("Roboto", 16))
        stock_label.place(x=30, y=60 + 40 * i)

    stock_frame = CTkFrame(master=app, width=250, height=380)
    stock_frame.grid(row=0, column=1, rowspan=2)

    stock_heading = CTkLabel(master=stock_frame, text="Watchlist", font=("Roboto", 24))
    stock_heading.place(x=80, y=5)

    portfolio_stocks = [
        {"name": "WALTON", "identifier": "WALTON"},
        {"name": "Grameenphone Ltd", "identifier": "GP"},
        {"name": "ACI Limited", "identifier": "ACI"},
        {"name": "DUTCHBANGLA Bank", "identifier": "DBBL"},
        {"name": "LankaBangla Finance", "identifier": "LANKABANGLA"}
    ]

    for i, stock_data in enumerate(portfolio_stocks):
        stock_name = stock_data["name"]
        stock_label = CTkLabel(master=stock_frame, text=stock_name, font=("Roboto", 16))
        stock_label.place(x=80, y=60 + 60 * i)

        eye = CTkImage(Image.open("./images/eye.png"), size=(17, 10))
        viw_btn = CTkButton(master=stock_frame, text="View", width=80, height=20, fg_color="#40e0d0",
                            hover_color="#cc00ff", image=eye,
                            command=lambda stock=stock_data["identifier"]: view(userid, stock))
        viw_btn.place(x=90, y=95 + 60 * i)
    lg = CTkImage(Image.open("./images/logout.png"), size=(20, 22))
    logout = CTkButton(master=port, text="Logout", fg_color="#40e0d0", hover_color="#e2062c", command=out, image=lg)
    logout.place(x=40, y=280)


def check(user, nid, phone, pass1, pass2, balance):
    if user != "" and nid != "" and phone != "" and pass1 != "" and balance != "":
        # Validate nid number (12 digits)
        if not re.match(r'^\d{12}$', nid):
            messagebox.showerror("Error", "Invalid nid number")
            return

        # Validate phone number (11 digits starting with 01)
        if not re.match(r'^01\d{9}$', phone):
            messagebox.showerror("Error", "Invalid phone number")
            return

        if pass1 == pass2:
            AddUser(user, nid, phone, pass1, balance)
            messagebox.showinfo("Done", "Registered Successfully")
            page1()
        else:
            messagebox.showerror("Error", "Passwords do not match")
    else:
        messagebox.showerror("Error", "Fill in all details")


def AddUser(full_name, nid_number, phone_number, password, initial_balance):
    user_sql = "INSERT INTO users (full_name, nid_number, phone_number, password) VALUES (?, ?, ?, ?)"
    cursor.execute(user_sql, (full_name, nid_number, phone_number, password))
    connection.commit()

    user_id = cursor.lastrowid

    wallet_sql = "INSERT INTO wallets (user_id, balance) VALUES (?, ?)"
    cursor.execute(wallet_sql, (user_id, initial_balance))
    connection.commit()

    print("User registered successfully!")


def login_check(phone_number, password):
    sql = "SELECT user_id FROM users WHERE phone_number = ? AND password = ?"
    cursor.execute(sql, (phone_number, password))
    result = cursor.fetchone()
    if result:
        frame.destroy()
        img_label.destroy()
        logged_in(result[0])
    else:
        messagebox.showerror("Error", "Invalid Credentials")


def backfnc():
    global frame
    global img_label
    frame.destroy()
    img_label.destroy()
    page1()


def login(): #Suchi
    global frame
    global img_label
    frame.destroy()
    frame = CTkFrame(master=app, width=200, height=400)
    frame.grid(row=0, column=1)

    img_logo = CTkImage(Image.open("./images/logo.png"), size=(100, 100))
    logo = CTkLabel(master=frame, image=img_logo, text="")
    logo.place(x=50, y=10)
    # Phone Number Entry
    phone_entry = CTkEntry(master=frame, placeholder_text="Phone Number")
    phone_entry.place(x=30, y=150)

    password_entry = CTkEntry(master=frame, placeholder_text="Password", show="*")
    password_entry.place(x=30, y=190)

    login_button = CTkButton(master=frame, text="Login", fg_color="#40e0d0", hover_color="#32cd32",
                             command=lambda: login_check(phone_entry.get(), password_entry.get()))
    login_button.place(x=30, y=230)

    back = CTkButton(master=frame, text="Back", fg_color="#40e0d0",
                     command=backfnc, hover_color="#ff4500")
    back.place(x=30, y=270)


def signup(): #Zarin
    global frame
    frame.destroy()
    frame = CTkFrame(master=app, width=200, height=400)
    frame.grid(row=0, column=1)

    img_logo = CTkImage(Image.open("./images/logo.png"), size=(70, 70))
    logo = CTkLabel(master=frame, image=img_logo, text="")
    logo.place(x=65, y=1)

    # UserName
    username = CTkEntry(master=frame, placeholder_text="Full Name")
    username.place(x=30, y=80)

    # nid Number Entry
    nid_entry = CTkEntry(master=frame, placeholder_text="NID Number")
    nid_entry.place(x=30, y=120)

    # Phone Number Entry
    phone_entry = CTkEntry(master=frame, placeholder_text="Phone Number")
    phone_entry.place(x=30, y=160)

    # Password Entry
    password_entry = CTkEntry(master=frame, placeholder_text="Password", show="*")
    password_entry.place(x=30, y=200)

    # Password Confirmation Entry
    password_confirm_entry = CTkEntry(master=frame, placeholder_text="Confirm Password", show="*")
    password_confirm_entry.place(x=30, y=240)

    # Balance
    balance = CTkEntry(master=frame, placeholder_text="Balance")
    balance.place(x=30, y=280)

    sign_btn = CTkButton(master=frame, text="Sign-Up", fg_color="#40e0d0", hover_color="#32cd32",
                         command=lambda: check(username.get(), nid_entry.get(), phone_entry.get(),
                                               password_confirm_entry.get(), password_entry.get(), balance.get()))
    sign_btn.place(x=30, y=320)
    bck = CTkButton(master=frame, text="Back", fg_color="#40e0d0",
                    command=backfnc, hover_color="#ff4500")
    bck.place(x=30, y=355)


def close():
    connection.close()
    app.destroy()


def change_theme():
    set_appearance_mode("light") if app._get_appearance_mode() == "dark" else set_appearance_mode("dark")


def page1(): #Afnan
    global frame
    global img_label
    frame.destroy()
    img_label.destroy()
    wallet_frame.destroy()
    port.destroy()
    stock_frame.destroy()
    img = CTkImage(Image.open("./images/login.jpg"), size=(300, 400))
    img_label = CTkLabel(master=app, image=img, text="")
    img_label.grid(row=0, column=0)

    frame = CTkFrame(master=app, width=200, height=400)
    frame.grid(row=0, column=1)

    img_logo = CTkImage(Image.open("./images/logo.png"), size=(100, 100))
    logo = CTkLabel(master=frame, image=img_logo, text="")
    logo.place(x=50, y=30)

    l_img = CTkImage(Image.open("./images/loginImg.png"), size=(21, 21))
    login_button = CTkButton(master=frame, text=" Login    ", fg_color="#40e0d0", hover_color="#009698", command=login,
                             image=l_img)
    login_button.place(x=30, y=170)
    s_img = CTkImage(Image.open("./images/signup.png"), size=(25, 21))
    sign_btn = CTkButton(master=frame, text="Sign-Up", fg_color="#40e0d0", hover_color="#009698", command=signup,
                         image=s_img)
    sign_btn.place(x=30, y=210)

    close_btn = CTkButton(master=frame, text="Close App", command=close, fg_color="#32cd32", hover_color="#e2062c")
    close_btn.place(x=30, y=260)

    t = CTkImage(dark_image=Image.open("./images/dark.png"), light_image=Image.open("./images/light.png"),
                 size=(70, 30))
    theme = CTkButton(master=frame, text="", image=t, fg_color="transparent", hover=False, width=66, height=34,
                      command=change_theme)
    theme.place(x=60, y=300)


page1()
app.mainloop()
print("""
 $$$$$$\                      $$\ $$\                     $$\     $$\                            $$$$$$\  $$\                                     $$\ 
$$  __$$\                     $$ |\__|                    $$ |    \__|                          $$  __$$\ $$ |                                    $$ |
$$ /  $$ | $$$$$$\   $$$$$$\  $$ |$$\  $$$$$$$\ $$$$$$\ $$$$$$\   $$\  $$$$$$\  $$$$$$$\        $$ /  \__|$$ | $$$$$$\   $$$$$$$\  $$$$$$\   $$$$$$$ |
$$$$$$$$ |$$  __$$\ $$  __$$\ $$ |$$ |$$  _____|\____$$\\_$$  _|  $$ |$$  __$$\ $$  __$$\       $$ |      $$ |$$  __$$\ $$  _____|$$  __$$\ $$  __$$ |
$$  __$$ |$$ /  $$ |$$ /  $$ |$$ |$$ |$$ /      $$$$$$$ | $$ |    $$ |$$ /  $$ |$$ |  $$ |      $$ |      $$ |$$ /  $$ |\$$$$$$\  $$$$$$$$ |$$ /  $$ |
$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |$$ |$$ |     $$  __$$ | $$ |$$\ $$ |$$ |  $$ |$$ |  $$ |      $$ |  $$\ $$ |$$ |  $$ | \____$$\ $$   ____|$$ |  $$ |
$$ |  $$ |$$$$$$$  |$$$$$$$  |$$ |$$ |\$$$$$$$\\$$$$$$$ | \$$$$  |$$ |\$$$$$$  |$$ |  $$ |      \$$$$$$  |$$ |\$$$$$$  |$$$$$$$  |\$$$$$$$\ \$$$$$$$ |
\__|  \__|$$  ____/ $$  ____/ \__|\__| \_______|\_______|  \____/ \__| \______/ \__|  \__|       \______/ \__| \______/ \_______/  \_______| \_______|
          $$ |      $$ |                                                                                                                              
          $$ |      $$ |                                                                                                                              
          \__|      \__|                                                                                                                              
""")
