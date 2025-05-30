import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from ttkbootstrap import Style

DATA_FILE = "data/data.json"

class RecipeManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("behold the stove")
        master.geometry("1024x768")

        # Style configuration
        style = ttk.Style()
        try:
            style = Style("flatly")  # or "darkly", "cyborg", etc.
        except tk.TclError:
            messagebox.showwarning("Theme Warning", "The 'breeze' theme is not available. Falling back to 'clam'.")
            style.theme_use("clam")

        style.configure("Treeview", font=("Segoe UI", 10), rowheight=20)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))

        self.data = self.load_data()

        self.left_frame = tk.Frame(master, width=250, height=600)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left_frame.pack_propagate(False)

        self.right_frame = tk.Frame(master)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree_container = tk.Frame(self.left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.tree = ttk.Treeview(tree_container, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.tag_configure("category", font=("Segoe UI", 10, "bold"))

        button_container = tk.Frame(self.left_frame)
        button_container.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        cat_btn_frame = tk.Frame(button_container)
        cat_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.add_cat_btn = ttk.Button(cat_btn_frame, text="Add Category", command=self.add_category)
        self.add_cat_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.edit_btn = ttk.Button(cat_btn_frame, text="Edit", command=self.edit_item)
        self.edit_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.del_btn = ttk.Button(cat_btn_frame, text="Delete", command=self.delete_item)
        self.del_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.add_rec_btn = ttk.Button(button_container, text="Add Recipe", command=self.add_recipe)
        self.add_rec_btn.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

        ttk.Label(self.right_frame, text="Recipe Details", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        self.recipe_details = tk.Text(self.right_frame, state=tk.DISABLED, font=("Segoe UI", 10))
        self.recipe_details.pack(fill=tk.BOTH, expand=True)

        self.populate_tree()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if "categories" in data and "recipes" in data:
                        return data
                except json.JSONDecodeError as e:
                    messagebox.showerror("Error", f"Error reading data file:\n{e}")
        return {"categories": [], "recipes": []}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data:\n{e}")

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cat in sorted(self.data["categories"]):
            cat_id = self.tree.insert("", tk.END, text=cat,
                                      values=("category", cat), open=False, tags=("category",))
            for recipe in sorted([r for r in self.data["recipes"] if r["category"] == cat],
                                 key=lambda r: r["title"]):
                self.tree.insert(cat_id, tk.END, text=recipe["title"],
                                 values=("recipe", cat))

    def get_selected_item(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def on_tree_select(self, event=None):
        item_id = self.get_selected_item()
        if not item_id:
            return
        item = self.tree.item(item_id)
        item_type = item.get("values", [None])[0]
        if item_type == "recipe":
            recipe_title = item["text"]
            category = item["values"][1]
            recipe = next((r for r in self.data["recipes"]
                        if r["title"] == recipe_title and r["category"] == category), None)
            if recipe:
                self.recipe_details.config(state=tk.NORMAL)
                self.recipe_details.delete("1.0", tk.END)

                # Define tags
                self.recipe_details.tag_configure("bold", font=("Segoe UI", 10, "bold"))
                self.recipe_details.tag_configure("title", font=("Segoe UI", 10, "bold italic"))

                # Title (bold italic)
                self.recipe_details.insert(tk.END, f"{recipe['title']}\n\n", "title")

                # Category label (bold)
                self.recipe_details.insert(tk.END, "Category: ", "bold")
                self.recipe_details.insert(tk.END, f"{recipe['category']}\n\n")

                # Ingredients label (bold)
                self.recipe_details.insert(tk.END, "Ingredients:\n", "bold")
                self.recipe_details.insert(tk.END, f"{recipe['ingredients']}\n\n")

                # Instructions label (bold)
                self.recipe_details.insert(tk.END, "Instructions:\n", "bold")
                self.recipe_details.insert(tk.END, f"{recipe['instructions']}")

                self.recipe_details.config(state=tk.DISABLED)
        else:
            self.recipe_details.config(state=tk.NORMAL)
            self.recipe_details.delete("1.0", tk.END)
            self.recipe_details.config(state=tk.DISABLED)

    def add_category(self):
        new_cat = simpledialog.askstring("Add Category", "Enter new category name:")
        if new_cat:
            if new_cat in self.data["categories"]:
                messagebox.showwarning("Warning", "This category already exists.")
                return
            self.data["categories"].append(new_cat)
            self.save_data()
            self.populate_tree()
            messagebox.showinfo("Success", f"Category '{new_cat}' added.")

    def edit_item(self):
        item_id = self.get_selected_item()
        if not item_id:
            messagebox.showwarning("Edit", "Please select an item to edit.")
            return
        item = self.tree.item(item_id)
        item_type = item.get("values", [None])[0]

        if item_type == "category":
            old_cat = item["text"]
            new_cat = simpledialog.askstring("Edit Category", "Update category name:", initialvalue=old_cat)
            if new_cat and new_cat != old_cat:
                if new_cat in self.data["categories"]:
                    messagebox.showwarning("Warning", "This category already exists.")
                    return
                index = self.data["categories"].index(old_cat)
                self.data["categories"][index] = new_cat
                for recipe in self.data["recipes"]:
                    if recipe["category"] == old_cat:
                        recipe["category"] = new_cat
                self.save_data()
                self.populate_tree()
                messagebox.showinfo("Success", f"Category updated to '{new_cat}'.")

        elif item_type == "recipe":
            recipe_title = item["text"]
            category = item["values"][1]
            recipe = next((r for r in self.data["recipes"]
                           if r["title"] == recipe_title and r["category"] == category), None)
            if not recipe:
                messagebox.showerror("Error", "Selected recipe not found.")
                return
            title = simpledialog.askstring("Edit Recipe", "Update Title:", initialvalue=recipe["title"])
            if not title:
                return
            ingredients = simpledialog.askstring("Edit Recipe", "Update Ingredients:", initialvalue=recipe["ingredients"])
            instructions = simpledialog.askstring("Edit Recipe", "Update Instructions:", initialvalue=recipe["instructions"])
            if ingredients is None or instructions is None:
                return
            recipe["title"] = title
            recipe["ingredients"] = ingredients
            recipe["instructions"] = instructions
            self.save_data()
            self.populate_tree()
            messagebox.showinfo("Success", f"Recipe updated to '{title}'.")

    def delete_item(self):
        item_id = self.get_selected_item()
        if not item_id:
            messagebox.showwarning("Delete", "Please select an item to delete.")
            return
        item = self.tree.item(item_id)
        item_type = item.get("values", [None])[0]

        if item_type == "category":
            cat = item["text"]
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{cat}' and all its recipes?"):
                if cat in self.data["categories"]:
                    self.data["categories"].remove(cat)
                self.data["recipes"] = [r for r in self.data["recipes"] if r["category"] != cat]
                self.save_data()
                self.populate_tree()
                messagebox.showinfo("Deleted", f"Category '{cat}' and its recipes have been deleted.")

        elif item_type == "recipe":
            recipe_title = item["text"]
            category = item["values"][1]
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete recipe '{recipe_title}'?"):
                self.data["recipes"] = [r for r in self.data["recipes"]
                                        if not (r["title"] == recipe_title and r["category"] == category)]
                self.save_data()
                self.populate_tree()
                messagebox.showinfo("Deleted", f"Recipe '{recipe_title}' deleted.")

    def add_recipe(self):
        item_id = self.get_selected_item()
        if not item_id:
            messagebox.showwarning("Add Recipe", "Please select a category to add a recipe under.")
            return
        item = self.tree.item(item_id)
        if item.get("values", [None])[0] == "recipe":
            parent_id = self.tree.parent(item_id)
            category = self.tree.item(parent_id)["text"]
        elif item.get("values", [None])[0] == "category":
            category = item["text"]
        else:
            messagebox.showwarning("Add Recipe", "Please select a category node.")
            return
        title = simpledialog.askstring("Add Recipe", "Enter Recipe Title:")
        if not title:
            return
        ingredients = simpledialog.askstring("Add Recipe", "Enter Ingredients:")
        instructions = simpledialog.askstring("Add Recipe", "Enter Instructions:")
        if ingredients is None or instructions is None:
            return
        new_recipe = {
            "title": title,
            "category": category,
            "ingredients": ingredients,
            "instructions": instructions
        }
        self.data["recipes"].append(new_recipe)
        self.save_data()
        self.populate_tree()
        messagebox.showinfo("Success", f"Recipe '{title}' added under '{category}'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeManagerApp(root)
    root.mainloop()
