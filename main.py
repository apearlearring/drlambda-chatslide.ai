import asyncio
import typer
from rich import print
from src.agent.chart_agent import ChartAgent
from src.utils.file_handler import FileHandler
from tenacity import retry, stop_after_attempt, wait_exponential

app = typer.Typer()
chart_agent = ChartAgent()
file_handler = FileHandler()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def async_process_file(data, command):
    """
    Async wrapper for processing file with retry logic
    """
    try:
        chart_config = await chart_agent.process_command(data, command)
        if not chart_config:
            raise ValueError("No chart configuration generated")
        return chart_config
    except Exception as e:
        print(f"[yellow]Retrying due to error: {str(e)}[/yellow]")
        raise

@app.command()
def process_file(
    file_path: str = typer.Argument(..., help="Path to the input file (CSV, Excel, or JSON)"),
    command: str = typer.Argument(..., help="Natural language command for chart generation")
):
    """
    Process a file and generate a chart based on the command
    """
    try:
        # Load and process the file
        print("[yellow]Loading file...[/yellow]")
        data = file_handler.load_file(file_path)
        
        print("[yellow]Processing command with AI...[/yellow]")
        
        # Create new event loop for async operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async operation with a timeout
            chart_config = loop.run_until_complete(
                asyncio.wait_for(async_process_file(data, command), timeout=60)
            )
            
            if not chart_config:
                raise ValueError("No chart configuration was generated")
                
            print("[green]Chart configuration generated successfully[/green]")
            print("Configuration:", chart_config)
            
            # Save and display the chart
            print("[yellow]Saving chart...[/yellow]")
            output_path = file_handler.save_chart(chart_config)
            print(f"[green]Chart saved successfully at: {output_path}[/green]")
            
        except asyncio.TimeoutError:
            print("[red]Operation timed out after 60 seconds[/red]")
            raise
        finally:
            loop.close()
            
    except Exception as e:
        print(f"[red]Error in process_file: {str(e)}[/red]")
        raise

@app.command()
def update_chart(
    command: str = typer.Argument(..., help="Natural language command to update the chart")
):
    """
    Update the existing chart based on new commands
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        updated_config = loop.run_until_complete(chart_agent.update_chart(command))
        loop.close()
        
        output_path = file_handler.save_chart(updated_config)
        print(f"[green]Chart updated successfully at: {output_path}[/green]")
        
    except Exception as e:
        print(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    app() 