import json
import os
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
from urllib.request import urlopen
from PIL import Image, ImageTk
from io import BytesIO

class Item:
    def __init__(self, title, genre, description, image_url):
        self.title = title
        self.genre = genre
        self.description = description
        self.image_url = image_url


class Movie(Item):
    def __init__(self, title, director, genre, length, description, image_url):
        super().__init__(title, genre, description, image_url)
        self.director = director
        self.length = length


class Game(Item):
    def __init__(self, title, developer, genre, platform, description, image_url):
        super().__init__(title, genre, description, image_url)
        self.developer = developer
        self.platform = platform

class Book(Item):
    def __init__(self, title, author, genre, pages, description, image_url):
        super().__init__(title, genre, description, image_url)
        self.author = author
        self.pages = pages

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
            if item_class == Movie:
                item = item_class(item_data.pop('title'), item_data.pop('director'), item_data.pop('genre'),
                                  item_data.pop('length'), item_data.pop('description'), item_data.pop('image_url'))
            elif item_class == Game:
                item = item_class(item_data.pop('title'), item_data.pop('developer'), item_data.pop('genre'),
                                  item_data.pop('platform'), item_data.pop('description'), item_data.pop('image_url'))
            elif item_class == Book:
                item = item_class(item_data.pop('title'), item_data.pop('author'), item_data.pop('genre'),
                                  item_data.pop('pages'), item_data.pop('description'), item_data.pop('image_url'))
            else:
                continue

            if 'image_url' in item_data:
                item.image_url = item_data['image_url']

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
        self.title("GW Collections")
        self.geometry("800x600")
        self.create_widgets()
        self.load_collections()
        self.selected_movie = None
        self.selected_game = None
        self.selected_book = None

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.LEFT, fill='both', expand=True)

        self.movie_container = ttk.Frame(self.notebook)
        self.movies_frame = ttk.Frame(self.movie_container)
        self.movies_frame.grid(row=0, column=0)
        self.add_movie_button = tk.Button(self.movie_container, text="Add Movie", command=self.open_add_movie_modal)
        self.add_movie_button.grid(row=1, column=0)

        self.game_container = ttk.Frame(self.notebook)
        self.games_frame = ttk.Frame(self.game_container)
        self.games_frame.grid(row=0, column=0) 
        self.add_movie_button = tk.Button(self.game_container, text="Add Game", command=self.open_add_game_modal)
        self.add_movie_button.grid(row=1, column=0)

        self.book_container = ttk.Frame(self.notebook)
        self.books_frame = ttk.Frame(self.book_container)
        self.books_frame.grid(row=0, column=0)
        self.add_book_button = tk.Button(self.book_container, text="Add Book", command=self.open_add_book_modal)
        self.add_book_button.grid(row=1, column=0)

        self.notebook.add(self.movie_container, text='Movies')
        self.notebook.add(self.game_container, text='Games')
        self.notebook.add(self.book_container, text='Books')

        self.right_frame = ttk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

        self.add_movie_button = tk.Button(self.movie_container, text="Add Movie", command=self.open_add_movie_modal)
        self.add_game_button = tk.Button(self.game_container, text="Add Game", command=self.open_add_game_modal)
        self.add_book_button = tk.Button(self.book_container, text="Add Book", command=self.open_add_book_modal)
        

        # Bind the event to load collections when a new tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)


    def tab_changed(self, event):
        selection = self.notebook.tab(self.notebook.select(), "text")

        if selection == 'Movies':
            self.add_movie_button.grid(row=1, column=0)
            self.add_game_button.pack_forget()
            self.add_book_button.pack_forget()

        elif selection == 'Games':
            self.add_movie_button.pack_forget()
            self.add_game_button.grid(row=1, column=0)
            self.add_book_button.pack_forget()


        elif selection == 'Books':
            self.add_movie_button.pack_forget()
            self.add_game_button.pack_forget()
            self.add_book_button.grid(row=1, column=0)

        for widget in self.right_frame.winfo_children():
            widget.destroy()

        


    def open_add_movie_modal(self):
        self.add_movie_modal = tk.Toplevel(self)
        self.add_movie_modal.grab_set()

        tk.Label(self.add_movie_modal, text="Title").grid(row=0, column=0)
        self.add_movie_title_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_title_entry.grid(row=0, column=1)

        tk.Label(self.add_movie_modal, text="Director").grid(row=1, column=0)
        self.add_movie_director_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_director_entry.grid(row=1, column=1)

        tk.Label(self.add_movie_modal, text="Genre").grid(row=2, column=0)
        self.add_movie_genre_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_genre_entry.grid(row=2, column=1)

        tk.Label(self.add_movie_modal, text="Length").grid(row=3, column=0)
        self.add_movie_length_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_length_entry.grid(row=3, column=1)

        tk.Label(self.add_movie_modal, text="Description").grid(row=4, column=0)
        self.add_movie_description_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_description_entry.grid(row=4, column=1)

        tk.Label(self.add_movie_modal, text="Poster URL").grid(row=5, column=0)
        self.add_movie_poster_url_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_poster_url_entry.grid(row=5, column=1)

        self.add_movie_submit_button = tk.Button(self.add_movie_modal, text="Add Movie", command=self.add_movie)
        self.add_movie_submit_button.grid(row=6, column=0, columnspan=2)
    
    def open_edit_movie_modal(self):
        self.add_movie_modal = tk.Toplevel(self)
        self.add_movie_modal.grab_set()

        tk.Label(self.add_movie_modal, text="Title").grid(row=0, column=0)
        self.add_movie_title_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_title_entry.insert(0, self.selected_movie.title)
        self.add_movie_title_entry.grid(row=0, column=1)

        tk.Label(self.add_movie_modal, text="Director").grid(row=1, column=0)
        self.add_movie_director_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_director_entry.insert(0, self.selected_movie.director)
        self.add_movie_director_entry.grid(row=1, column=1)

        tk.Label(self.add_movie_modal, text="Genre").grid(row=2, column=0)
        self.add_movie_genre_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_genre_entry.insert(0, self.selected_movie.genre)
        self.add_movie_genre_entry.grid(row=2, column=1)

        tk.Label(self.add_movie_modal, text="Length").grid(row=3, column=0)
        self.add_movie_length_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_length_entry.insert(0, self.selected_movie.length)
        self.add_movie_length_entry.grid(row=3, column=1)

        tk.Label(self.add_movie_modal, text="Description").grid(row=4, column=0)
        self.add_movie_description_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_description_entry.insert(0, self.selected_movie.description)
        self.add_movie_description_entry.grid(row=4, column=1)

        tk.Label(self.add_movie_modal, text="Image URL").grid(row=5, column=0)
        self.add_movie_poster_url_entry = tk.Entry(self.add_movie_modal)
        self.add_movie_poster_url_entry.insert(0, self.selected_movie.image_url)
        self.add_movie_poster_url_entry.grid(row=5, column=1)

        # Adding the "Cancel" and "Edit Movie" buttons at the bottom
        edit_button = tk.Button(self.add_movie_modal, text="Cancel", command=self.close_edit_movie_modal)
        edit_button.grid(row=6, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 
        
        delete_button = tk.Button(self.add_movie_modal, text="Edit Movie", command=self.edit_movie)
        delete_button.grid(row=6, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding

    def close_edit_movie_modal(self):
        self.add_movie_modal.destroy()

    def edit_movie(self):
        # Extract the updated data from the entry fields
        new_title = self.add_movie_title_entry.get()
        new_director = self.add_movie_director_entry.get()
        new_genre = self.add_movie_genre_entry.get()
        new_length = self.add_movie_length_entry.get()
        new_description = self.add_movie_description_entry.get()
        new_image_url = self.add_movie_poster_url_entry.get()

        # Create a new Movie object with the updated data
        updated_movie = Movie(new_title, new_director, new_genre, new_length, new_description, new_image_url)

        # Update the movie in the collections
        self.collection_manager.update_item('movies', self.selected_movie, updated_movie)

        # Close the edit modal
        self.close_edit_movie_modal()

        # Reload movie details
        #self.display_movie_details()

        self.selected_movie = None

        # Clearing the right_frame 
        for widget in self.right_frame.winfo_children():
            widget.destroy()


        self.refresh_movie_list(deployed=1)


    def add_movie(self):
        title = self.add_movie_title_entry.get()
        director = self.add_movie_director_entry.get()
        genre = self.add_movie_genre_entry.get()
        length = self.add_movie_length_entry.get()
        description = self.add_movie_description_entry.get()
        poster_url = self.add_movie_poster_url_entry.get()
        movie = Movie(title, director, genre, length, description, poster_url)
        self.collection_manager.add_item('movies', movie)
        self.add_movie_modal.destroy()
        self.refresh_movie_list(deployed=1)

    def refresh_movie_list(self, search_term = None, deployed = None):
        for widget in self.movies_frame.winfo_children():
            if isinstance(widget, tk.Listbox):
                widget.destroy()
            if isinstance(widget, tk.Label):
                widget.destroy()

        if not deployed:
            self.search_box = tk.Entry(self.movies_frame)
            self.search_box.pack()
        self.search_box.bind("<KeyRelease>", self.search_movie)

        label = tk.Label(self.movies_frame, text="Movies List")
        label.pack()

        self.movies_listbox = tk.Listbox(self.movies_frame)
        self.movies_listbox.pack(fill='both', expand=True)
        if not search_term:
            for movie in self.collection_manager.collections['movies']:
                self.movies_listbox.insert(tk.END, movie.title)
        else:         
            for movie in self.collection_manager.collections['movies']:
                if search_term in movie.title:
                    self.movies_listbox.insert(tk.END, movie.title)
        self.movies_listbox.bind('<<ListboxSelect>>', self.display_movie_details)

    def search_movie(self, event):
        search_term = self.search_box.get()
        print(search_term)
        self.refresh_movie_list(search_term, 1)
        
        

    def display_movie_details(self, event):
        # Get the current selection from the ListBox
        selection = event.widget.curselection()

        if selection:
            index = selection[0]
            movie = self.collection_manager.collections['movies'][index]
            self.selected_movie = movie  # Store the selected movie object

            # Clearing the right_frame before adding new details
            for widget in self.right_frame.winfo_children():
                widget.destroy()

            # Show movie image
            try:
                photo = self.show_image(movie.image_url)
                image_label = tk.Label(self.right_frame, image=photo)
                image_label.image = photo  # keep a reference to the image
                image_label.grid(row=0, column=2, rowspan=48)  # added
            except Exception as e:
                print(f"Failed to load image: {e}")

            # Displaying Movie Details
            tk.Label(self.right_frame, text="\n\n\nTitle: " + movie.title).grid(row=0, column=0, columnspan=2)  # changed
            tk.Label(self.right_frame, text="Director: " + movie.director).grid(row=1, column=0, columnspan=2)  # changed
            tk.Label(self.right_frame, text="Genre: " + movie.genre).grid(row=2, column=0, columnspan=2)  # changed
            tk.Label(self.right_frame, text="Length: " + str(movie.length)).grid(row=3, column=0, columnspan=2)  # changed
            tk.Label(self.right_frame, text="Description: " + movie.description).grid(row=4, column=0, columnspan=2)  # changed

            # Adding the "Edit Movie" and "Delete Movie" buttons at the bottom
            edit_button = tk.Button(self.right_frame, text="Edit Movie", command=self.open_edit_movie_modal)
            edit_button.grid(row=5, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 

            delete_button = tk.Button(self.right_frame, text="Delete Movie", command=self.delete_movie)
            delete_button.grid(row=5, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding

    def delete_movie(self):

        # Show confirmation dialog
        confirm = messagebox.askokcancel("Delete Movie", f"Are you sure you want to delete '{self.selected_movie.title}'?")
        
        # If the user confirms the deletion
        if confirm:
            # Remove the movie from the collection
            self.collection_manager.remove_item('movies', self.selected_movie)
            # Update the ListBox to reflect the deletion
            self.refresh_movie_list(deployed=1)
            # Reset the selected movie to None after deletion
            self.selected_movie = None

            # Clearing the right_frame 
            for widget in self.right_frame.winfo_children():
                widget.destroy()

        

    def open_add_game_modal(self):
        add_game_modal = tk.Toplevel(self)

        tk.Label(add_game_modal, text="Title").grid(row=0, column=0)
        tk.Label(add_game_modal, text="Developer").grid(row=1, column=0)
        tk.Label(add_game_modal, text="Genre").grid(row=2, column=0)
        tk.Label(add_game_modal, text="Platform").grid(row=3, column=0)
        tk.Label(add_game_modal, text="Description").grid(row=4, column=0)
        tk.Label(add_game_modal, text="Image URL").grid(row=5, column=0)

        title_entry = tk.Entry(add_game_modal)
        title_entry.grid(row=0, column=1)
        developer_entry = tk.Entry(add_game_modal)
        developer_entry.grid(row=1, column=1)
        genre_entry = tk.Entry(add_game_modal)
        genre_entry.grid(row=2, column=1)
        platform_entry = tk.Entry(add_game_modal)
        platform_entry.grid(row=3, column=1)
        description_entry = tk.Entry(add_game_modal)
        description_entry.grid(row=4, column=1)
        image_url_entry = tk.Entry(add_game_modal)
        image_url_entry.grid(row=5, column=1)

        add_button = tk.Button(add_game_modal, text="Add Game", command=lambda: self.add_game(
            title_entry.get(),
            developer_entry.get(),
            genre_entry.get(),
            platform_entry.get(),
            description_entry.get(),
            image_url_entry.get(),
            add_game_modal
        ))
        add_button.grid(row=6, column=0, columnspan=2)

    def add_game(self, title, developer, genre, platform, description, image_url, add_game_modal):
        game = Game(title, developer, genre, platform, description, image_url)
        self.collection_manager.add_item('games', game)
        add_game_modal.destroy()
        self.refresh_game_list(deployed=1)

    def open_edit_game_modal(self):
        self.add_game_modal = tk.Toplevel(self)
        self.add_game_modal.grab_set()

        tk.Label(self.add_game_modal, text="Title").grid(row=0, column=0)
        self.add_game_title_entry = tk.Entry(self.add_game_modal)
        self.add_game_title_entry.insert(0, self.selected_game.title)
        self.add_game_title_entry.grid(row=0, column=1)

        tk.Label(self.add_game_modal, text="Developer").grid(row=1, column=0)
        self.add_game_developer_entry = tk.Entry(self.add_game_modal)
        self.add_game_developer_entry.insert(0, self.selected_game.developer)
        self.add_game_developer_entry.grid(row=1, column=1)

        tk.Label(self.add_game_modal, text="Genre").grid(row=2, column=0)
        self.add_game_genre_entry = tk.Entry(self.add_game_modal)
        self.add_game_genre_entry.insert(0, self.selected_game.genre)
        self.add_game_genre_entry.grid(row=2, column=1)

        tk.Label(self.add_game_modal, text="Platform").grid(row=3, column=0)
        self.add_game_platform_entry = tk.Entry(self.add_game_modal)
        self.add_game_platform_entry.insert(0, self.selected_game.platform)
        self.add_game_platform_entry.grid(row=3, column=1)

        tk.Label(self.add_game_modal, text="Description").grid(row=4, column=0)
        self.add_game_description_entry = tk.Entry(self.add_game_modal)
        self.add_game_description_entry.insert(0, self.selected_game.description)
        self.add_game_description_entry.grid(row=4, column=1)

        tk.Label(self.add_game_modal, text="Image URL").grid(row=5, column=0)
        self.add_game_image_url_entry = tk.Entry(self.add_game_modal)
        self.add_game_image_url_entry.insert(0, self.selected_game.image_url)
        self.add_game_image_url_entry.grid(row=5, column=1)

        # Adding the "Cancel" and "Edit Game" buttons at the bottom
        edit_button = tk.Button(self.add_game_modal, text="Cancel", command=self.close_edit_game_modal)
        edit_button.grid(row=6, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 
        
        delete_button = tk.Button(self.add_game_modal, text="Edit Game", command=self.edit_game)
        delete_button.grid(row=6, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding

    def close_edit_game_modal(self):
        self.add_game_modal.destroy()

    def edit_game(self):
        print("inside")
        # Extract the updated data from the entry fields
        new_title = self.add_game_title_entry.get()
        new_developer = self.add_game_developer_entry.get()
        new_genre = self.add_game_genre_entry.get()
        new_platform = self.add_game_platform_entry.get()
        new_description = self.add_game_description_entry.get()
        new_image_url = self.add_game_image_url_entry.get()

        # Create a new Game object with the updated data
        updated_game = Game(new_title, new_developer, new_genre, new_platform, new_description, new_image_url)

        # Update the game in the collections
        self.collection_manager.update_item('games', self.selected_game, updated_game)

        # Close the edit modal
        self.close_edit_game_modal()

        # Reload movie details
        #self.display_movie_details()

        self.selected_game = None

        # Clearing the right_frame 
        for widget in self.right_frame.winfo_children():
            widget.destroy()


        self.refresh_game_list(deployed=1)


    def refresh_game_list(self, game_search_term = None, deployed = None):
        for widget in self.games_frame.winfo_children():
            if isinstance(widget, tk.Listbox):
                widget.destroy()
            if isinstance(widget, tk.Label):
                widget.destroy()

        if not deployed:
            self.game_search_box = tk.Entry(self.games_frame)
            self.game_search_box.pack()
        self.game_search_box.bind("<KeyRelease>", self.search_game)

        label = tk.Label(self.games_frame, text="Games List")
        label.pack()

        self.games_listbox = tk.Listbox(self.games_frame)
        self.games_listbox.pack(fill='both', expand=True)
        if not game_search_term:
            for game in self.collection_manager.collections['games']:
                self.games_listbox.insert(tk.END, game.title)
        else:         
            for game in self.collection_manager.collections['games']:
                if game_search_term in game.title:
                    self.games_listbox.insert(tk.END, game.title)
        self.games_listbox.bind('<<ListboxSelect>>', self.display_game_details)

    def search_game(self, event):
        game_search_term = self.game_search_box.get()
        print(game_search_term)
        self.refresh_game_list(game_search_term, 1)

    def display_game_details(self, event):
        # Get the current selection from the ListBox
        selection = event.widget.curselection()

        if selection:
            index = selection[0]
            game = self.collection_manager.collections['games'][index]
            self.selected_game = game  # Store the selected game object

            # Clearing the right_frame before adding new details
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            
            # Show game image
            try:
                photo = self.show_image(game.image_url)
                image_label = tk.Label(self.right_frame, image=photo)
                image_label.image = photo  # keep a reference to the image
                image_label.grid(row=0, column=2, rowspan=48)
            except Exception as e:
                print(f"Failed to load image: {e}")

            # Displaying Game Details
            tk.Label(self.right_frame, text="\n\nTitle: " + game.title).grid(row=0, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Developer: " + game.developer).grid(row=1, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Genre: " + game.genre).grid(row=2, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Platform: " + str(game.platform)).grid(row=3, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Description: " + game.description).grid(row=4, column=0, columnspan=2)

            # Adding the "Edit Game" and "Delete Game" buttons at the bottom
            edit_button = tk.Button(self.right_frame, text="Edit Game", command=self.open_edit_game_modal)
            edit_button.grid(row=5, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 

            delete_button = tk.Button(self.right_frame, text="Delete Game", command=self.delete_game)
            delete_button.grid(row=5, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding


    def delete_game(self):

        # Show confirmation dialog
        confirm = messagebox.askokcancel("Delete Game", f"Are you sure you want to delete '{self.selected_game.title}'?")
        
        # If the user confirms the deletion
        if confirm:
            # Remove the game from the collection
            self.collection_manager.remove_item('games', self.selected_game)
            # Update the ListBox to reflect the deletion
            self.refresh_game_list(deployed=1)
            # Reset the selected movie to None after deletion
            self.selected_game = None

            # Clearing the right_frame 
            for widget in self.right_frame.winfo_children():
                widget.destroy()


    def open_add_book_modal(self):
        add_book_modal = tk.Toplevel(self)

        tk.Label(add_book_modal, text="Title").grid(row=0, column=0)
        tk.Label(add_book_modal, text="Author").grid(row=1, column=0)
        tk.Label(add_book_modal, text="Genre").grid(row=2, column=0)
        tk.Label(add_book_modal, text="Pages").grid(row=3, column=0)
        tk.Label(add_book_modal, text="Description").grid(row=4, column=0)
        tk.Label(add_book_modal, text="Image URL").grid(row=5, column=0)

        title_entry = tk.Entry(add_book_modal)
        title_entry.grid(row=0, column=1)
        author_entry = tk.Entry(add_book_modal)
        author_entry.grid(row=1, column=1)
        genre_entry = tk.Entry(add_book_modal)
        genre_entry.grid(row=2, column=1)
        pages_entry = tk.Entry(add_book_modal)
        pages_entry.grid(row=3, column=1)
        description_entry = tk.Entry(add_book_modal)
        description_entry.grid(row=4, column=1)
        image_url_entry = tk.Entry(add_book_modal)
        image_url_entry.grid(row=5, column=1)

        add_button = tk.Button(add_book_modal, text="Add Book", command=lambda: self.add_book(
            title_entry.get(),
            author_entry.get(),
            genre_entry.get(),
            pages_entry.get(),
            description_entry.get(),
            image_url_entry.get(),
            add_book_modal
        ))
        add_button.grid(row=6, column=0, columnspan=2)

    def add_book(self, title, author, genre, pages, description, image_url, add_book_modal):
        book = Book(title, author, genre, pages, description, image_url)
        self.collection_manager.add_item('books', book)
        add_book_modal.destroy()
        self.refresh_book_list()

    def open_edit_book_modal(self):
        self.add_book_modal = tk.Toplevel(self)
        self.add_book_modal.grab_set()

        tk.Label(self.add_book_modal, text="Title").grid(row=0, column=0)
        self.add_book_title_entry = tk.Entry(self.add_book_modal)
        self.add_book_title_entry.insert(0, self.selected_book.title)
        self.add_book_title_entry.grid(row=0, column=1)

        tk.Label(self.add_book_modal, text="Author").grid(row=1, column=0)
        self.add_book_author_entry = tk.Entry(self.add_book_modal)
        self.add_book_author_entry.insert(0, self.selected_book.author)
        self.add_book_author_entry.grid(row=1, column=1)

        tk.Label(self.add_book_modal, text="Genre").grid(row=2, column=0)
        self.add_book_genre_entry = tk.Entry(self.add_book_modal)
        self.add_book_genre_entry.insert(0, self.selected_book.genre)
        self.add_book_genre_entry.grid(row=2, column=1)

        tk.Label(self.add_book_modal, text="Pages").grid(row=3, column=0)
        self.add_book_pages_entry = tk.Entry(self.add_book_modal)
        self.add_book_pages_entry.insert(0, self.selected_book.pages)
        self.add_book_pages_entry.grid(row=3, column=1)

        tk.Label(self.add_book_modal, text="Description").grid(row=4, column=0)
        self.add_book_description_entry = tk.Entry(self.add_book_modal)
        self.add_book_description_entry.insert(0, self.selected_book.description)
        self.add_book_description_entry.grid(row=4, column=1)

        tk.Label(self.add_book_modal, text="Image URL").grid(row=5, column=0)
        self.add_book_image_url_entry = tk.Entry(self.add_book_modal)
        self.add_book_image_url_entry.insert(0, self.selected_book.image_url)
        self.add_book_image_url_entry.grid(row=5, column=1)

        # Adding the "Cancel" and "Edit Book" buttons at the bottom
        edit_button = tk.Button(self.add_book_modal, text="Cancel", command=self.close_edit_book_modal)
        edit_button.grid(row=6, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 
        
        delete_button = tk.Button(self.add_book_modal, text="Edit Book", command=self.edit_book)
        delete_button.grid(row=6, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding

    def close_edit_book_modal(self):
        self.add_book_modal.destroy()

    def edit_book(self):
        # Extract the updated data from the entry fields
        new_title = self.add_book_title_entry.get()
        new_author = self.add_book_author_entry.get()
        new_genre = self.add_book_genre_entry.get()
        new_pages = self.add_book_pages_entry.get()
        new_description = self.add_book_description_entry.get()
        new_image_url = self.add_book_image_url_entry.get()

        # Create a new Game object with the updated data
        updated_book = Book(new_title, new_author, new_genre, new_pages, new_description, new_image_url)

        # Update the game in the collections
        self.collection_manager.update_item('books', self.selected_book, updated_book)

        # Close the edit modal
        self.close_edit_book_modal()

        # Reload movie details
        #self.display_movie_details()

        self.selected_book = None

        # Clearing the right_frame 
        for widget in self.right_frame.winfo_children():
            widget.destroy()


        self.refresh_book_list()

    def refresh_book_list(self):
        for widget in self.books_frame.winfo_children():
            widget.destroy()
        label = tk.Label(self.books_frame, text="Book List")
        label.pack()
        self.books_listbox = tk.Listbox(self.books_frame)
        self.books_listbox.pack(fill='both', expand=True)
        for book in self.collection_manager.collections['books']:
            self.books_listbox.insert(tk.END, book.title)
        self.books_listbox.bind('<<ListboxSelect>>', self.display_book_details)

    def display_book_details(self, event):
        # Get the current selection from the ListBox
        selection = event.widget.curselection()

        if selection:
            index = selection[0]
            book = self.collection_manager.collections['books'][index]
            self.selected_book = book  # Store the selected book object

            # Clearing the right_frame before adding new details
            for widget in self.right_frame.winfo_children():
                widget.destroy()

            # Show book image
            try:
                photo = self.show_image(book.image_url)
                image_label = tk.Label(self.right_frame, image=photo)
                image_label.image = photo  # keep a reference to the image
                image_label.grid(row=0, column=2, rowspan=48)
            except Exception as e:
                print(f"Failed to load image: {e}")


            # Displaying Book Details
            tk.Label(self.right_frame, text="\n\nTitle: " + book.title).grid(row=0, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Author: " + book.author).grid(row=1, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Genre: " + book.genre).grid(row=2, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Pages: " + str(book.pages)).grid(row=3, column=0, columnspan=2)
            tk.Label(self.right_frame, text="Description: " + book.description).grid(row=4, column=0, columnspan=2)

            # Adding the "Edit Book" and "Delete Book" buttons at the bottom
            edit_button = tk.Button(self.right_frame, text="Edit Book", command=self.open_edit_book_modal)
            edit_button.grid(row=5, column=0, pady=10, padx=10)  # update row value accordingly and add some padding 

            delete_button = tk.Button(self.right_frame, text="Delete Book", command=self.delete_book)
            delete_button.grid(row=5, column=1, pady=10, padx=10)  # update row and column value accordingly and add some padding



    def delete_book(self):

        # Show confirmation dialog
        confirm = messagebox.askokcancel("Delete Book", f"Are you sure you want to delete '{self.selected_book.title}'?")
        
        # If the user confirms the deletion
        if confirm:
            # Remove the movie from the collection
            self.collection_manager.remove_item('books', self.selected_book)
            # Update the ListBox to reflect the deletion
            self.refresh_book_list()
            # Reset the selected movie to None after deletion
            self.selected_book = None

            # Clearing the right_frame 
            for widget in self.right_frame.winfo_children():
                widget.destroy()

    def show_image(self, image_url):
        response = urlopen(image_url)
        image_data = response.read()
        image = Image.open(BytesIO(image_data))
        image = image.resize((300, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        return photo
    
    
    def load_collections(self):
        self.refresh_movie_list()
        self.refresh_game_list()
        self.refresh_book_list()




file_manager = FileManager({
    'movies': 'movies.json',
    'games': 'games.json',
    'books': 'books.json'
})

manager = CollectionManager(file_manager)
app = GUI(manager)
app.mainloop()

