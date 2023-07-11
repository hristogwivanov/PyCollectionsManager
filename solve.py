import json
import os
import tkinter as tk
from tkinter import messagebox

class Item:
    def __init__(self, title):
        self.title = title

class Movie(Item):
    def __init__(self, title, director):
        super().__init__(title)
        self.director = director

class Game(Item):
    def __init__(self, title, developer):
        super().__init__(title)
        self.developer = developer

class Book(Item):
    def __init__(self, title, author):
        super().__init__(title)
        self.author = author

class FileManager:
    def __init__(self, file_names):
        self.file_names = file_names

    def load_data(self):
        collections = {}
        for collection, file_name in self.file_names.items():
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    collections[collection] = self.load_collection(json.load(f))
            else:
                collections[collection] = []
        return collections

    def load_collection(self, collection_data):
        collection = []
        for item_data in collection_data:
            item_class = globals()[item_data.pop('class')]
            item = item_class(**item_data)
            collection.append(item)
        return collection

    def save_data(self, collections):
        for collection, items in collections.items():
            with open(self.file_names[collection], 'w') as f:
                json.dump(self.save_collection(items), f)

    def save_collection(self, collection):
        collection_data = []
        for item in collection:
            item_data = item.__dict__.copy()
            item_data['class'] = item.__class__.__name__
            collection_data.append(item_data)
        return collection_data


class CollectionManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.collections = self.file_manager.load_data()

    def add_item(self, collection, item):
        self.collections[collection].append(item)
        self.file_manager.save_data(self.collections)

    def remove_item(self, collection, item):
        self.collections[collection].remove(item)
        self.file_manager.save_data(self.collections)

    def search(self, term):
        results = {}
        for key, value_list in self.collections.items():
            results[key] = [item for item in value_list if term.lower() in item.title.lower()]
        return results

    def update_item(self, collection, old_item, new_item):
        index = self.collections[collection].index(old_item)
        self.collections[collection][index] = new_item
        self.file_manager.save_data(self.collections)


class GUI(tk.Tk):
    def __init__(self, collection_manager):
        tk.Tk.__init__(self)
        self.collection_manager = collection_manager
        self.create_widgets()

    def create_widgets(self):
        self.search_term_entry = tk.Entry(self)
        self.search_term_entry.pack()

        self.search_button = tk.Button(self, text="Search", command=self.search)
        self.search_button.pack()

        self.results_text = tk.Text(self)
        self.results_text.pack()

    def search(self):
        term = self.search_term_entry.get()
        results = self.collection_manager.search(term)
        self.results_text.delete('1.0', tk.END)
        for collection, items in results.items():
            self.results_text.insert(tk.END, f"{collection}:\n")
            for item in items:
                self.results_text.insert(tk.END, f"  {item.title}\n")


if __name__ == "__main__":
    file_manager = FileManager({
        'movies': 'movies.json',
        'games': 'games.json',
        'books': 'books.json'
    })
    manager = CollectionManager(file_manager)
    app = GUI(manager)
    app.mainloop()
