from tkinter import *
from tkinter import messagebox as mb, simpledialog as sd
from tkinter import ttk
import pandas as pd
from tkcalendar import DateEntry
import sqlite3 as db
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables required for the app
data_entry_color = '#608BC1'
data_label_color = "#133E87"
main_bg = "#000"
exit_btn_color = "#C62E2E"
filter_btn_color =""
plot_btn_color = "#EC8305"
edit_btn_color="#789DBC"

# Create the sqlite Database
def database_init():
    conn = db.connect('expenses.db')
    c = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS expenses(
        ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        date DATETIME,
        expense FLOAT,
        category TEXT,
        description TEXT 
    )
    """
    c.execute(query)
    conn.commit()
    conn.close()


database_init()


# Creating GUI with  Tkinter

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.configure(padx=20, pady=20)
        self.root.geometry("1200x700")
        self.root.resizable(0, 0)

        # Show widgets
        self.create_dataframe()
        self.create_tree_frame()
        self.list_expenses()

        # handle the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def add_expense(self):
        date = self.dateEntry.get()
        expense =self.amountEntry.get()
        category = self.category_combobox.get()
        description = self.descriptionEntry.get()

        if date and expense and category and description:
            values = [date, expense, category, description]
            self.expense_table.insert('', 'end', values=values)
            conn = db.connect('expenses.db')
            c = conn.cursor()
            query = """
                        INSERT INTO expenses(date, expense, category, description) VALUES (?, ?, ?, ?)
                        """
            c.execute(query, (date, expense, category, description))
            conn.commit()
            conn.close()

            mb.showinfo("Success", "Expense added successfully!")
            self.clear_text()
        else:

            mb.showerror("Empty Field!"," Please fill out all the fields before pressing the add button." )

        print(date, expense, category, description)

    def list_expenses(self):
        conn = db.connect('expenses.db')
        c = conn.cursor()
        # Clear existing items in the Treeview
        for item in self.expense_table.get_children():
            self.expense_table.delete(item)

        all_data = c.execute("SELECT ID, date, expense, category, description FROM expenses")
        data = all_data.fetchall()

        for values in data:
            # print(values)
            self.expense_table.insert('', END, iid= values[0],values=values[1:])
        conn.close()

    def view_expenses(self):
        conn = db.connect('expenses.db')
        df = pd.read_sql_query("SELECT date, expense, description FROM expenses", conn)
        conn.close()
        if not df.empty:
            self.show_expenses_window(df)
        else:
            mb.showinfo("No expenses", "No expenses recorded")

    def show_expenses_window(self, df):
        conn = db.connect('expenses.db')
        c = conn.cursor()

        # Create a toplevel window
        expenses_window = Toplevel(self.root)
        expenses_window.title("Expenses")
        expenses_window.geometry("1050x300")

        expense_frame = Frame(expenses_window,bd=4, bg='#071952')
        expense_frame.place(x=0, y=0, width=1050, height=200)

        y_scroll = Scrollbar(expense_frame, orient=VERTICAL)
        x_scroll = Scrollbar(expense_frame, orient=HORIZONTAL)

        expense_tree = ttk.Treeview(expense_frame, columns=list(df.columns), show='headings', yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side=RIGHT, fill=Y)
        y_scroll.config(command=self.expense_table.yview)
        x_scroll.pack(side=BOTTOM, fill=X)
        x_scroll.config(command=self.expense_table.xview)
        expense_tree.pack(expand=True, fill='both')

        # Add column headings
        for col in df.columns:
            expense_tree.heading(col, text=col)
            expense_tree.column(col, anchor='center')

        # Insert data into tree
        for index, row in df.iterrows():
            expense_tree.insert('', 'end', values=list(row))

        # Add a scrollbar
        # scrollbar = ttk.Scrollbar(expenses_window, orient="vertical", command=expense_tree.yview)
        # expense_tree.configure(yscrollcommand=scrollbar.set)
        # scrollbar.pack(side='right', fill='y')

        # Resize the columns to fit the content
        for col in df.columns:
            expense_tree.column(col, width=100, anchor='center')

        total_query = """
        SELECT sum(expense) FROM expenses
        """
        c.execute(total_query)

        total = c.fetchall()[0][0]

        amtLabel = Label(expenses_window, text=f"Your total expenditure is {total}", font=("arial", 15),fg="white", bg="#071952")
        amtLabel.place(x=0, y=200, width=1050, height=80)

        conn.commit()
        conn.close()

    def on_select(self, event):
        selected_items = self.expense_table.selection()
        if selected_items:
            selected_item = selected_items[0]
            item_values = self.expense_table.item(selected_item, 'values')

    def edit_selected_expense(self):

        conn = db.connect('expenses.db')
        c = conn.cursor()
        if not self.expense_table.selection():
            mb.showerror("No record selected", "Please select a record to continue!")
        current_selected_expense = self.expense_table.selection()
        selected_expense_details = self.expense_table.selection()[0]
        item_values = self.expense_table.item(selected_expense_details, 'values')

        current_date, current_expense, current_category, current_desc = item_values
        if selected_expense_details:
            selected_expense_id = current_selected_expense[0]
            edit_window = Toplevel(self.root)
            edit_window.title("Edit Expense")
            # Date Label and Entry
            date_label = Label(edit_window, text="Date", font=('arial', 15, 'bold'))
            date_label.grid(row=0, column=0, padx=10, pady=10)
            date_entry = DateEntry(edit_window, font=('arial', 15, 'bold'))
            date_entry.grid(row=0, column=1, padx=10, pady=10)
            date_entry.set_date(current_date)

            # Expense Label and Entry
            expense_label = Label(edit_window, text="Expenditure", font=('arial', 15, 'bold'))
            expense_label.grid(row=1, column=0, padx=10, pady=10)
            expense_entry = Entry(edit_window, font=('arial', 15, 'bold'))
            expense_entry.grid(row=1, column=1, padx=10, pady=10)
            expense_entry.insert(0, current_expense)

            # Category Label and Entry
            category_label = Label(edit_window, text="Category", font=('arial', 15, 'bold'))
            category_label.grid(row=2, column=0, padx=10, pady=10)
            category_combobox = ttk.Combobox(edit_window,
                                             values=["Food", "Transport", "Rent", "Shopping", "Gifts", "Entertainment",
                                                     "Health", "Education", "Others"], font=('arial', 15, 'bold'))
            category_combobox.grid(row=2, column=1, padx=10, pady=10)
            category_combobox.set(current_category)

            # Description Label and Entry
            description_label = Label(edit_window, text="Description", font=('arial', 15, 'bold'))
            description_label.grid(row=3, column=0, padx=10, pady=10)
            description_entry = Entry(edit_window, font=('arial', 15, 'bold'))
            description_entry.grid(row=3, column=1, padx=10, pady=10)
            description_entry.insert(0, current_desc)


            def save_changes():
                updated_date = date_entry.get()
                updated_expense = expense_entry.get()
                updated_category = category_combobox.get()
                updated_desc = description_entry.get()

                # Only update if values are changes
                updates = {}

                if updated_date != current_date:
                    updates['date'] = updated_date
                if updated_expense != current_expense:
                    updates['expense'] = updated_expense
                if updated_category != current_category:
                    updates['category'] = updated_category
                if updated_desc != current_desc:
                    updates['description'] = updated_desc

                if updates:
                    set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
                    values = list(updates.values())
                    values.append(selected_expense_id)

                    c.execute(f"UPDATE expenses SET {set_clause} WHERE ID = ?", values)
                    conn.commit()
                    mb.showinfo("Success", "Expense updated successfully!")
                    self.list_expenses()  # Refresh the table
                    edit_window.destroy()
                else:
                    mb.showinfo("No Changes", "No changes were made to the expense.")

            save_button = Button(edit_window, text="Save Changes", command=save_changes)
            save_button.grid(row=4, columnspan=2, padx=10, pady=10)

            edit_window.protocol("WM_DELETE_WINDOW", lambda: (
            edit_window.destroy(), conn.close()))  # Close db connection when window is closed

    def delete_selected_expense(self):
        conn = db.connect('expenses.db')
        c = conn.cursor()
        if not self.expense_table.selection():
            mb.showerror("No record selected","Please select a record to continue!")

        current_selected_expense = self.expense_table.selection()

        if current_selected_expense:
        #     item_values = self.expense_table.item(current_selected_expense, 'values')
            expense_id = int(current_selected_expense[0])
            # print(type(expense_id))

            sure = mb.askyesno("Are you sure?", "Are you sure you want to delete the selected record?")

            if sure:
                c.execute("DELETE FROM expenses WHERE ID=?", (expense_id,))

                conn.commit()
                conn.close()
                self.list_expenses()
                mb.showinfo("Successful Deletion!", "The record you wanted to delete has been deleted successfullly.")

            else:
                mb.showinfo("Cancelled", "Task aborted.No expense was deleted!")

    def clear_text(self):
        self.amountEntry.delete("0", "end")
        self.category_combobox.delete("0", "end")
        self.descriptionEntry.delete("0", "end")

    def clear_all_expenses(self):

        sure = mb.askyesno("Are you sure?", "Are you sure that you want to delete all the expenses from the database?")
        conn = db.connect("expenses.db")
        c = conn.cursor()
        if sure:
            query = """
            DELETE  FROM expenses
            """
            c.execute(query)
            conn.commit()
            conn.close()
            for item in self.expense_table.get_children():
                self.expense_table.delete(item)
            mb.showinfo("All expenses deleted!", "All the expenses have been deleted successfully!")
        else:
            mb.showinfo("Cancelled", "Task aborted.No expense was deleted!")

    def visualize_bar_plot(self):
        conn = db.connect('expenses.db')
        df = pd.read_sql_query("SELECT category, SUM(expense) AS total_expense FROM expenses GROUP BY category", conn)
        conn.close()

        if df.empty:
            mb.showinfo("No Data", "No expenses recorded to visualize!")
            return

        # Create a bar plot
        plt.figure(figsize=(10,6))
        sns.barplot(data=df, x='category', y='total_expense',hue="category" ,palette='viridis')

        plt.xlabel("Category")
        plt.ylabel("Total Expense")
        plt.title("Total Expense by Category")

        # Creating toplevel window

        bar_window = Toplevel(self.root)
        bar_window.title("Bar Plot of Expenses")

        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(plt.gcf(), master=bar_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close()

    def visualize_line_plot(self):
        conn = db.connect('expenses.db')
        df = pd.read_sql_query("SELECT date, SUM(expense) AS total_expense FROM expenses GROUP BY date", conn)
        conn.close()

        if df.empty:
            mb.showinfo("No Data", "No expenses recorded to visualize!")
            return

        # Create a bar plot
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='date', y='total_expense', marker='o')

        plt.xlabel("Date")
        plt.ylabel("Total Expense")
        plt.title("Total Expense Over Time")

        # Creating toplevel window

        line_window = Toplevel(self.root)
        line_window.title("Line Plot of Expenses")
    

        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(plt.gcf(), master=line_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close()

    def exit_application(self):
        conn = db.connect('expenses.db')
        conn.close()
        self.root.destroy()

    def create_tree_frame(self):
        self.tree_frame = Frame(self.root, bg=data_label_color)
        self.tree_frame.place(x=0, y=0, height=370, width=830)

        label = Label(self.tree_frame,text="EXPENSE TRACKER", font=('arial', 20, 'bold'),fg="black")
        label.pack(fill=BOTH)

        y_scroll = Scrollbar(self.tree_frame, orient=VERTICAL)
        x_scroll = Scrollbar(self.tree_frame, orient=HORIZONTAL)

        cols = ['Date', 'Expense', 'Category', 'Description']

        self.expense_table = ttk.Treeview(self.tree_frame, selectmode=BROWSE,columns=cols, height=300, yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.expense_table.bind('<<TreeviewSelect>>', self.on_select)

        y_scroll.config(command=self.expense_table.yview)
        x_scroll.config(command=self.expense_table.xview)

        x_scroll.pack(side=BOTTOM, fill=X)
        y_scroll.pack(side=RIGHT, fill=Y)

        # Hide the default column
        self.expense_table['show'] = 'headings'

        for c in cols:
            self.expense_table.heading(c, text=c.title())
        self.expense_table.pack(fill=BOTH)

    # def filter_expense(self, event):
    #     conn = db.connect("expenses.db")
    #     c = conn.cursor()
    #
    #
    #
    # def create_filter_frame(self):
    #     self.filter_frame = Frame(self.root, bg=data_entry_color)
    #     self.filter_frame.place(x=870, y=50, height=280, width=280)
    #
    #     filterLabel = Label(self.filter_frame, text="Filter by:",font=('arial', 15, 'bold'), bg=data_label_color, fg="white", width=12)
    #     filterLabel.place(x=65, y=80)
    #
    #     self.choice = StringVar()
    #     choices = [
    #         "Date",
    #         "Expense",
    #         "Category"
    #     ]
    #
    #     filter_box = ttk.Combobox(self.filter_frame, values=choices, textvariable=self.choice, font=('arial',15,'bold'))
    #     filter_box.current(0)
    #     filter_box.place(x=20, y=140)
    # Create the dataEntry Frame

    def create_dataframe(self):
        # self.frame_1 = Frame(self.root, bg=data_entry_color)
        # self.frame_1.place(x=0, y=250, relheight=0.50, relwidth=1.0)

        # Creating 2 different frames inside the Data Entry frame
        self.data_entry_frame = Frame(self.root, bg=data_entry_color)
        self.data_entry_frame.place(x=0,y=370,relheight=0.50, relwidth=0.50)

        self.btn_frame = Frame(self.root, bg=data_entry_color)
        self.btn_frame.place(x=590, y=370, relheight=0.50, relwidth=0.50)
        self.btn_frame.columnconfigure(0, weight=1)
        self.btn_frame.columnconfigure(1, weight=1)
        # Create widgets in the data entry frames

        # Date
        self.dateLabel = Label(self.data_entry_frame, text="Date",font=('arial', 15, 'bold'), bg=data_label_color, fg="white", width=12)
        self.dateLabel.grid(row=0, column=0, padx=10, pady=10, sticky=(W))

        self.dateEntry = DateEntry(self.data_entry_frame,font=('arial',15,'bold'))
        self.dateEntry.grid(row=0,column=1,padx=10,pady=7,sticky=(W))

        # Expense
        expense = DoubleVar()
        self.amountLabel = Label(self.data_entry_frame, text="Expenditure", font=('arial', 15, 'bold'), bg=data_label_color,
                          fg="white", width=12)
        self.amountLabel.grid(row=1, column=0, padx=10, pady=10, sticky=(W))

        self.amountEntry = Entry(self.data_entry_frame, textvariable=expense ,font=('arial', 15, 'bold'))
        self.amountEntry.grid(row=1, column=1, padx=10, pady=7, sticky=(W))

        # Category
        option = StringVar()
        options=["Food", "Transport", "Rent", "Shopping", "Gifts", "Entertainment", "Health", "Education", "Others"]
        self.categoryLabel = Label(self.data_entry_frame, text="Category", font=('arial', 15, 'bold'), bg=data_label_color,
                          fg="white", width=12)
        self.categoryLabel.grid(row=2, column=0, padx=10, pady=10, sticky=(W))

        self.category_combobox = ttk.Combobox(self.data_entry_frame, values=options, textvariable=option, font=('arial', 15, 'bold'))
        self.category_combobox.current(0)

        self.category_combobox.grid(row=2, column=1, padx=10, pady=7, sticky=(W))

        # Description
        description= StringVar()
        self.descriptionLabel = Label(self.data_entry_frame, text="Description", font=('arial', 15, 'bold'), bg=data_label_color,
                          fg="white", width=12)
        self.descriptionLabel.grid(row=3, column=0, padx=10, pady=10, sticky=(W))

        self.descriptionEntry = Entry(self.data_entry_frame, textvariable=description,font=('arial', 15, 'bold'))
        self.descriptionEntry.grid(row=3, column=1, padx=10, pady=7, sticky=(W))


        # Button Frame Widgets
        add_btn = Button(self.btn_frame, text="Add Expense",font=('arial',15,'bold'),bg=data_label_color,fg="white", width=20
                         , command=self.add_expense)
        add_btn.grid(row=0, column=0,padx=10,pady=10,sticky=(W))

        view_btn = Button(self.btn_frame, text="View Expenses",font=('arial',15,'bold'),bg=data_label_color,fg="white", width=20,
                          command=self.view_expenses)
        view_btn.grid(row=0, column=1,padx=10,pady=10,sticky=(W))

        line_btn = Button(self.btn_frame, text="Visualize Line-graph", font=('arial', 15, 'bold'), bg=plot_btn_color,
                         fg="white", width=20, command=self.visualize_line_plot)
        line_btn.grid(row=1, column=0, padx=10, pady=10, sticky=(W))

        bar_btn = Button(self.btn_frame, text="Visualize Bar-graph", font=('arial', 15, 'bold'), bg=plot_btn_color,
                          fg="white", width=20, command=self.visualize_bar_plot)
        bar_btn.grid(row=1, column=1, padx=10, pady=10, sticky=(W))

        edit_btn = Button(self.btn_frame, text="Edit Selected Expense", font=('arial', 15, 'bold'), bg=edit_btn_color,
                           fg="white", width=20, command=self.edit_selected_expense)
        edit_btn.grid(row=2, column=0, padx=10, pady=10, sticky=(W))

        del_btn = Button(self.btn_frame, text="Delete Selected Expense", font=('arial', 15, 'bold'), bg=edit_btn_color,
                          fg="white", width=20, command=self.delete_selected_expense)
        del_btn.grid(row=2, column=1, padx=10, pady=10, sticky=(W))

        clear_btn = Button(self.btn_frame, text="Delete All Expenses", font=('arial', 15, 'bold'), bg=exit_btn_color,
                          fg="white", width=20, command=self.clear_all_expenses)
        clear_btn.grid(row=3, column=0, padx=10, pady=10, sticky=(W))

        exit_btn = Button(self.btn_frame, text="Exit", font=('arial', 15, 'bold'), bg=exit_btn_color,
                          fg="white", width=20, command=self.exit_application)
        exit_btn.grid(row=3, column=1, padx=10, pady=10, sticky=(W))


# Run the application
if __name__ == "__main__":
    root = Tk()
    app = ExpenseTrackerApp(root)
    root.update()
    root.mainloop()
