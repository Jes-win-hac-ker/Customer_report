import customtkinter as ctk
import mysql.connector
import csv
from CTkMessagebox import CTkMessagebox

# --- DB Connection ---
db = mysql.connector.connect(
    host="localhost",
    user="customer_report",  # change your user
    password="1234",  # your password
    database="customer_report"
)
cursor = db.cursor()

# --- Main App ---
def main_app():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("IT Service Manager")
    root.geometry("900x600")

    # --- Main layout: left menu, right content ---
    menu_frame = ctk.CTkFrame(root, width=200)
    menu_frame.pack(side="left", fill="y", padx=10, pady=10)

    content_frame = ctk.CTkFrame(root)
    content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # --- Menu Buttons ---
    ctk.CTkButton(menu_frame, text="Submit Report", command=lambda: load_submit(content_frame)).pack(pady=10, fill="x")
    ctk.CTkButton(menu_frame, text="Search Report", command=lambda: load_search(content_frame)).pack(pady=10, fill="x")
    ctk.CTkButton(menu_frame, text="Update Report", command=lambda: load_update(content_frame)).pack(pady=10, fill="x")
    ctk.CTkButton(menu_frame, text="Delete Report", command=lambda: load_delete(content_frame)).pack(pady=10, fill="x")

    # Load Submit form by default
    load_submit(content_frame)

    root.mainloop()
    cursor.close()
    db.close()

# --- Clear frame ---
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# --- Submit Page ---
def load_submit(frame):
    clear_frame(frame)

    name_entry = create_entry(frame, "Customer Name")
    phone_entry = create_entry(frame, "Phone Number")
    problem_textbox = create_textbox(frame, "Problem Description")
    date_given = create_entry(frame, "Date Given (YYYY-MM-DD)")
    date_diag = create_entry(frame, "Date Diagnosed (YYYY-MM-DD)")
    date_ret = create_entry(frame, "Date Returned (YYYY-MM-DD)")

    def submit():
        sql = """
        INSERT INTO reports (customer_name, phone_number, problem_description, date_given, date_diagnosed, date_returned)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            name_entry.get(),
            phone_entry.get(),
            problem_textbox.get("1.0", "end").strip(),
            date_given.get(),
            date_diag.get(),
            date_ret.get()
        )
        cursor.execute(sql, values)
        db.commit()
        CTkMessagebox(title="Success", message="Report Submitted!", icon="check")
        clear_submit()

    def clear_submit():
        name_entry.delete(0, "end")
        phone_entry.delete(0, "end")
        problem_textbox.delete("1.0", "end")
        date_given.delete(0, "end")
        date_diag.delete(0, "end")
        date_ret.delete(0, "end")

    ctk.CTkButton(frame, text="Submit Report", command=submit).pack(pady=10)
    ctk.CTkButton(frame, text="Clear Form", command=clear_submit).pack(pady=5)

# --- Search Page ---
def load_search(frame):
    clear_frame(frame)

    search_entry = create_entry(frame, "Exact Name or Phone (Case Sensitive)")

    results_box = create_textbox(frame, "Results")
    results_box.configure(state="disabled")

    def search():
        term = search_entry.get()
        sql = """
        SELECT * FROM reports WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (term, term)
        cursor.execute(sql, values)
        results = cursor.fetchall()

        results_box.configure(state="normal")
        results_box.delete("1.0", "end")

        if results:
            for row in results:
                results_box.insert("end", f"ID: {row[0]}\nName: {row[1]}\nPhone: {row[2]}\nProblem: {row[3]}\nDate Given: {row[4]}\nDate Diagnosed: {row[5]}\nDate Returned: {row[6]}\n{'-'*50}\n")
        else:
            results_box.insert("end", "No records found.")

        results_box.configure(state="disabled")

    def show_all():
        sql = "SELECT * FROM reports"
        cursor.execute(sql)
        results = cursor.fetchall()

        results_box.configure(state="normal")
        results_box.delete("1.0", "end")

        for row in results:
            results_box.insert("end", f"ID: {row[0]}\nName: {row[1]}\nPhone: {row[2]}\nProblem: {row[3]}\nDate Given: {row[4]}\nDate Diagnosed: {row[5]}\nDate Returned: {row[6]}\n{'-'*50}\n")

        results_box.configure(state="disabled")

    def export_csv():
        term = search_entry.get()
        sql = """
        SELECT * FROM reports WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (term, term)
        cursor.execute(sql, values)
        results = cursor.fetchall()

        if results:
            with open("exported_report.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Customer Name", "Phone Number", "Problem", "Date Given", "Date Diagnosed", "Date Returned"])
                for row in results:
                    writer.writerow(row)
            CTkMessagebox(title="Success", message="Exported to exported_report.csv", icon="check")
        else:
            CTkMessagebox(title="Info", message="No data to export.", icon="info")

    ctk.CTkButton(frame, text="Search", command=search).pack(pady=10)
    ctk.CTkButton(frame, text="Show All Records", command=show_all).pack(pady=5)
    ctk.CTkButton(frame, text="Export to CSV", command=export_csv).pack(pady=5)
    ctk.CTkButton(frame, text="Clear Form", command=lambda: search_entry.delete(0, "end")).pack(pady=5)

# --- Update Page ---
def load_update(frame):
    clear_frame(frame)

    update_term_entry = create_entry(frame, "Exact Name or Phone to Update (Case Sensitive)")
    problem_textbox = create_textbox(frame, "New Problem Description")
    date_ret = create_entry(frame, "New Date Returned (YYYY-MM-DD)")

    def update():
        sql = """
        UPDATE reports SET
            problem_description = %s,
            date_returned = %s
        WHERE BINARY customer_name = %s OR BINARY phone_number = %s
        """
        values = (
            problem_textbox.get("1.0", "end").strip(),
            date_ret.get(),
            update_term_entry.get(),
            update_term_entry.get()
        )
        cursor.execute(sql, values)
        db.commit()
        CTkMessagebox(title="Success", message="Report Updated!", icon="check")
        clear_update()

    def clear_update():
        update_term_entry.delete(0, "end")
        problem_textbox.delete("1.0", "end")
        date_ret.delete(0, "end")

    ctk.CTkButton(frame, text="Update Report", command=update).pack(pady=10)
    ctk.CTkButton(frame, text="Clear Form", command=clear_update).pack(pady=5)

# --- Delete Page ---
def load_delete(frame):
    clear_frame(frame)

    delete_entry = create_entry(frame, "Exact Name or Phone to Delete (Case Sensitive)")

    def delete():
        result = CTkMessagebox(title="Confirm Delete", message=f"Are you sure you want to delete record: {delete_entry.get()}?", icon="warning", option_1="Yes", option_2="Cancel")

        if result.get() == "Yes":
            sql = """
            DELETE FROM reports WHERE BINARY customer_name = %s OR BINARY phone_number = %s
            """
            values = (delete_entry.get(), delete_entry.get())
            cursor.execute(sql, values)
            db.commit()
            CTkMessagebox(title="Deleted", message="Record deleted!", icon="check")
            delete_entry.delete(0, "end")

    ctk.CTkButton(frame, text="Delete Report", command=delete).pack(pady=10)
    ctk.CTkButton(frame, text="Clear Form", command=lambda: delete_entry.delete(0, "end")).pack(pady=5)

# --- Helper ---
def create_entry(parent, label_text):
    label = ctk.CTkLabel(parent, text=label_text)
    label.pack(pady=5)
    entry = ctk.CTkEntry(parent, placeholder_text=label_text)
    entry.pack(pady=5)
    return entry

def create_textbox(parent, label_text):
    label = ctk.CTkLabel(parent, text=label_text)
    label.pack(pady=5)
    textbox = ctk.CTkTextbox(parent, width=600, height=300)
    textbox.pack(pady=5)
    return textbox

# --- Run ---
if __name__ == "__main__":
    main_app()
