#!/usr/bin/env python3
"""
DevSync GUI - Graphical User Interface
Modern window-based interface for deployment automation
"""

import sys
import threading
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Import main deploy components
try:
    from deploy import (
        DeployAutomation, Version, VersionManager, 
        GitManager, ProjectValidator, ChangelogManager
    )
except ImportError:
    print("Error: deploy.py not found in current directory")
    sys.exit(1)


class DevSyncGUI:
    """Main GUI application for DevSync"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DevSync - Deployment Automation")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Status variables
        self.current_version = "0.0.0"
        self.next_version = "0.0.0"
        self.branch = ""
        self.username = ""
        self.project_files = {}
        self.deploy_thread = None
        self.is_deploying = False
        
        # Setup UI
        self.setup_ui()
        self.load_project_info()
        
    def setup_ui(self):
        """Create and arrange UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="🚀 DevSync", 
            font=("Arial", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Deployment Automation Tool",
            font=("Arial", 10)
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Left panel - Info and controls
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Project Info Frame
        info_frame = ttk.LabelFrame(left_panel, text="Project Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Version info
        ttk.Label(info_frame, text="Current Version:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.current_version_label = ttk.Label(info_frame, text="0.0.0", font=("Arial", 12, "bold"), foreground="green")
        self.current_version_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Next Version:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.next_version_label = ttk.Label(info_frame, text="0.0.0", font=("Arial", 12, "bold"), foreground="blue")
        self.next_version_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="Branch:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.branch_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.branch_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(info_frame, text="User:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.user_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.user_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Deployment Controls Frame
        controls_frame = ttk.LabelFrame(left_panel, text="Deployment Options", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Version bump type
        ttk.Label(controls_frame, text="Version Bump:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bump_type = tk.StringVar(value="patch")
        bump_frame = ttk.Frame(controls_frame)
        bump_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Radiobutton(bump_frame, text="Patch", variable=self.bump_type, value="patch").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bump_frame, text="Minor", variable=self.bump_type, value="minor").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(bump_frame, text="Major", variable=self.bump_type, value="major").pack(side=tk.LEFT, padx=5)
        
        # Custom version
        ttk.Label(controls_frame, text="Custom Version:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_version_var = tk.StringVar()
        custom_entry = ttk.Entry(controls_frame, textvariable=self.custom_version_var, width=15)
        custom_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(controls_frame, text="(optional)", font=("Arial", 8), foreground="gray").grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        # Options
        self.skip_changelog_var = tk.BooleanVar()
        ttk.Checkbutton(controls_frame, text="Skip Changelog", variable=self.skip_changelog_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.no_merge_var = tk.BooleanVar()
        ttk.Checkbutton(controls_frame, text="Skip Auto-Merge", variable=self.no_merge_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Deploy button
        self.deploy_button = ttk.Button(
            controls_frame,
            text="🚀 Start Deployment",
            command=self.start_deployment,
            style="Accent.TButton"
        )
        self.deploy_button.grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Project Files Frame
        files_frame = ttk.LabelFrame(left_panel, text="Project Files", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for files
        tree_frame = ttk.Frame(files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_tree = ttk.Treeview(tree_frame, columns=("status",), show="tree headings", height=8)
        self.files_tree.heading("#0", text="File")
        self.files_tree.heading("status", text="Status")
        self.files_tree.column("#0", width=200)
        self.files_tree.column("status", width=100)
        
        scrollbar_files = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=scrollbar_files.set)
        
        self.files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_files.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Right panel - Progress and logs
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(right_panel, text="Deployment Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.step_label = ttk.Label(progress_frame, text="Ready to deploy", font=("Arial", 10, "bold"))
        self.step_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="0%", font=("Arial", 9))
        self.progress_label.pack(anchor=tk.W)
        
        # Logs Frame
        logs_frame = ttk.LabelFrame(right_panel, text="Deployment Logs", padding="10")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            logs_frame,
            height=20,
            width=50,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
    def log(self, message: str, level: str = "info"):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": "black",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        
        tag = f"log_{level}"
        self.log_text.tag_config(tag, foreground=colors.get(level, "black"))
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def update_progress(self, step: int, total: int, message: str):
        """Update progress bar and step label"""
        percentage = (step / total) * 100
        self.progress_var.set(percentage)
        self.progress_label.config(text=f"{int(percentage)}% - Step {step}/{total}")
        self.step_label.config(text=message)
        self.log(f"Step {step}/{total}: {message}")
        self.root.update_idletasks()
        
    def load_project_info(self):
        """Load and display project information"""
        try:
            version_mgr = VersionManager()
            current_version = version_mgr.read_version()
            self.current_version = str(current_version)
            self.current_version_label.config(text=self.current_version)
            
            git_mgr = GitManager(Path.cwd())
            self.username = git_mgr.username
            self.branch = f"develop-{git_mgr.username}"
            
            self.user_label.config(text=self.username)
            self.branch_label.config(text=self.branch)
            
            # Calculate next version
            bump_type = self.bump_type.get()
            next_version = current_version.bump(bump_type)
            self.next_version = str(next_version)
            self.next_version_label.config(text=self.next_version)
            
            # Load project files
            validator = ProjectValidator(Path.cwd())
            required = validator.check_required_files()
            recommended = validator.check_recommended_files()
            self.project_files = {**required, **recommended}
            
            # Update files tree
            self.files_tree.delete(*self.files_tree.get_children())
            for file, exists in self.project_files.items():
                status = "✓ Found" if exists else "✗ Missing"
                tag = "found" if exists else "missing"
                item = self.files_tree.insert("", tk.END, text=file, values=(status,), tags=(tag,))
                self.files_tree.tag_configure("found", foreground="green")
                self.files_tree.tag_configure("missing", foreground="red")
            
            self.log("Project information loaded", "success")
            
        except Exception as e:
            self.log(f"Error loading project info: {str(e)}", "error")
            messagebox.showerror("Error", f"Failed to load project information:\n{str(e)}")
    
    def prompt_changelog(self, version: str) -> Optional[str]:
        """Show changelog input dialog (must be called from main thread)"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Changelog Entry - Version {version}")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.focus_set()
        
        result = {"value": None}
        
        # Header
        header = ttk.Label(
            dialog,
            text=f"Enter changelog for version {version}",
            font=("Arial", 12, "bold")
        )
        header.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(
            dialog,
            text="Enter your changelog entries (one per line):",
            font=("Arial", 9)
        )
        instructions.pack(pady=5)
        
        # Example
        example = ttk.Label(
            dialog,
            text="Example:\n  - Added new feature\n  - Fixed bug\n  - Improved performance",
            font=("Arial", 8),
            foreground="gray"
        )
        example.pack(pady=5)
        
        # Text area
        text_frame = ttk.Frame(dialog, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        changelog_text = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        changelog_text.pack(fill=tk.BOTH, expand=True)
        changelog_text.focus()
        
        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def save_changelog():
            content = changelog_text.get("1.0", tk.END).strip()
            if content:
                result["value"] = content
            dialog.destroy()
        
        def skip_changelog():
            result["value"] = None
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_changelog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Skip", command=skip_changelog).pack(side=tk.LEFT, padx=5)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window()
        return result["value"]
    
    def start_deployment(self):
        """Start deployment in a separate thread"""
        if self.is_deploying:
            messagebox.showwarning("Warning", "Deployment already in progress!")
            return
        
        # Get deployment options
        bump_type = self.bump_type.get()
        custom_version = self.custom_version_var.get().strip()
        skip_changelog = self.skip_changelog_var.get()
        auto_merge = not self.no_merge_var.get()
        
        # Proactively ask about custom version if field is blank
        if not custom_version:
            answer = messagebox.askyesnocancel("Custom Version", "Do you want to set the next version manually?")
            if answer is None:
                self.log("Deployment cancelled by user", "warning")
                return
            if answer:
                # Prompt for the version string in a dialog
                while True:
                    manual = tk.simpledialog.askstring(
                        "Set Version",
                        "Enter the new version (e.g., 1.2.3, 2.0.0rc1):",
                        parent=self.root
                    )
                    if manual is None:
                        self.log("Deployment cancelled by user", "warning")
                        return
                    manual = manual.strip()
                    try:
                        Version.parse(manual)
                    except Exception as e:
                        messagebox.showerror("Invalid Version", f"Error: {e}\nPlease use X.Y.Z[optional suffix], e.g. 1.0.0, 2.0.0rc1.")
                        continue
                    custom_version = manual
                    self.custom_version_var.set(manual)
                    break
        # If the user declined, just continue with bump_type
        
        # Validate again
        if custom_version:
            try:
                Version.parse(custom_version)
            except ValueError:
                messagebox.showerror("Error", f"Invalid version format: {custom_version}")
                return
        
        # Disable button
        self.deploy_button.config(state=tk.DISABLED, text="Deploying...")
        self.is_deploying = True
        
        # Clear logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start deployment thread
        self.deploy_thread = threading.Thread(
            target=self.run_deployment,
            args=(bump_type, custom_version, skip_changelog, auto_merge),
            daemon=True
        )
        self.deploy_thread.start()
    
    def run_deployment(self, bump_type: str, custom_version: Optional[str], skip_changelog: bool, auto_merge: bool):
        """Run deployment process"""
        try:
            automation = DeployAutomation()
            version_mgr = VersionManager()
            git_mgr = GitManager(Path.cwd())
            validator = ProjectValidator(Path.cwd())
            changelog_mgr = ChangelogManager(Path.cwd())
            
            total_steps = 12
            step = 0
            
            # Step 0: Validate project structure
            step += 1
            self.update_progress(step, total_steps, "Validating project structure")
            is_valid, warnings = validator.validate()
            if not is_valid:
                raise Exception("Missing required files. Please create them before deploying.")
            if warnings:
                for warning in warnings:
                    self.log(f"Warning: {warning}", "warning")
            time.sleep(0.3)
            
            # Step 1: Validate repository
            step += 1
            self.update_progress(step, total_steps, "Validating Git repository")
            if not git_mgr.validate_repo():
                raise Exception("Not a valid Git repository or remote not configured")
            time.sleep(0.3)
            
            # Step 2: Configure user
            step += 1
            self.update_progress(step, total_steps, "Configuring Git user")
            git_mgr.configure_user()
            time.sleep(0.3)
            
            # Step 3: Create branch
            step += 1
            branch_name = f"develop-{git_mgr.username}"
            self.update_progress(step, total_steps, f"Creating branch: {branch_name}")
            git_mgr.create_and_checkout_branch(branch_name)
            time.sleep(0.3)
            
            # Step 4: Bump or set version
            step += 1
            if custom_version:
                self.update_progress(step, total_steps, f"Setting version to {custom_version}")
                new_version = version_mgr.set_version(custom_version)
            else:
                self.update_progress(step, total_steps, f"Bumping version ({bump_type})")
                new_version = version_mgr.bump_version(bump_type)
            
            self.next_version = str(new_version)
            self.root.after(0, lambda: self.next_version_label.config(text=self.next_version))
            time.sleep(0.3)
            
            # Step 5: Changelog
            step += 1
            changelog_entry = None
            if not skip_changelog:
                self.update_progress(step, total_steps, "Waiting for changelog entry")
                self.log("Opening changelog dialog...", "info")
                
                # Schedule dialog in main thread and wait for result
                result_container = {"value": None, "done": False}
                
                def show_dialog():
                    try:
                        result_container["value"] = self.prompt_changelog(str(new_version))
                    except Exception as e:
                        self.log(f"Changelog dialog error: {e}", "error")
                        result_container["value"] = None
                    finally:
                        result_container["done"] = True
                
                # Schedule on main thread
                self.root.after(0, show_dialog)
                
                # Wait for completion (with timeout)
                timeout = 300  # 5 minutes max
                elapsed = 0
                while not result_container["done"] and elapsed < timeout:
                    time.sleep(0.1)
                    elapsed += 0.1
                    # Process pending events
                    try:
                        self.root.update_idletasks()
                    except:
                        break
                
                changelog_entry = result_container["value"]
                
                if changelog_entry:
                    from datetime import datetime
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    changelog_mgr.add_entry(str(new_version), date_str, changelog_entry)
                    self.log("Changelog updated", "success")
                else:
                    self.log("Changelog skipped", "warning")
            else:
                self.update_progress(step, total_steps, "Skipping changelog")
                time.sleep(0.2)
            
            # Step 6: Commit and push
            step += 1
            self.update_progress(step, total_steps, "Committing and pushing changes")
            commit_msg = f"chore: bump version to {new_version}"
            if not git_mgr.commit_and_push(commit_msg, branch_name):
                raise Exception("Failed to push changes")
            self.log("Changes pushed successfully", "success")
            time.sleep(0.5)
            
            # Step 7: Trigger CI/CD
            step += 1
            self.update_progress(step, total_steps, "Triggering CI/CD pipeline")
            time.sleep(0.5)
            
            # Step 8: Wait for pipeline
            step += 1
            self.update_progress(step, total_steps, "Waiting for CI/CD pipeline")
            for i in range(5):
                self.update_progress(step, total_steps, f"Waiting for CI/CD pipeline{'.' * ((i % 3) + 1)}")
                time.sleep(1)
            self.log("CI/CD pipeline completed", "success")
            
            # Step 9: Merge to main
            if auto_merge:
                step += 1
                self.update_progress(step, total_steps, "Merging to main branch")
                if not git_mgr.merge_to_main(branch_name):
                    raise Exception("Failed to merge to main")
                self.log("Merged to main successfully", "success")
                time.sleep(0.5)
            else:
                step += 1
                self.update_progress(step, total_steps, "Skipping auto-merge")
                self.log("Auto-merge skipped", "warning")
            
            # Step 10: Create tag
            step += 1
            self.update_progress(step, total_steps, "Creating tag and release")
            tag_name = f"v{new_version}"
            git_mgr.create_tag(tag_name, f"Release {new_version}")
            self.log(f"Tag {tag_name} created", "success")
            time.sleep(0.5)
            
            # Complete
            step = total_steps
            self.update_progress(step, total_steps, "Deployment completed successfully!")
            self.log("=" * 50, "success")
            self.log(f"Deployment completed!", "success")
            self.log(f"Version: {self.current_version} → {new_version}", "success")
            self.log(f"Branch: {branch_name}", "success")
            self.log(f"Tag: {tag_name}", "success")
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Deployment completed successfully!\n\n"
                f"Version: {self.current_version} → {new_version}\n"
                f"Branch: {branch_name}\n"
                f"Tag: {tag_name}"
            ))
            
            # Reload project info
            self.root.after(0, self.load_project_info)
            
        except Exception as e:
            self.log(f"Deployment failed: {str(e)}", "error")
            self.root.after(0, lambda: messagebox.showerror("Deployment Failed", str(e)))
        finally:
            self.is_deploying = False
            self.root.after(0, lambda: self.deploy_button.config(state=tk.NORMAL, text="🚀 Start Deployment"))
    
    def on_bump_type_change(self, *args):
        """Update next version when bump type changes"""
        if not self.is_deploying:
            try:
                version_mgr = VersionManager()
                current_version = version_mgr.read_version()
                bump_type = self.bump_type.get()
                next_version = current_version.bump(bump_type)
                self.next_version = str(next_version)
                self.next_version_label.config(text=self.next_version)
            except:
                pass


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DevSync - Graphical UI")
    parser.add_argument("--cli", action="store_true", help="Use CLI mode instead of GUI")
    
    args = parser.parse_args()
    
    if args.cli:
        # Fallback to terminal UI if requested
        print("CLI mode not implemented. Use deploy.py for command-line interface.")
        sys.exit(1)
    
    # Create and run GUI
    root = tk.Tk()
    app = DevSyncGUI(root)
    
    # Update next version when bump type changes
    app.bump_type.trace('w', app.on_bump_type_change)
    
    root.mainloop()


if __name__ == "__main__":
    main()
