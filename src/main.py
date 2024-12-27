#!/usr/bin/env python3

import click
from loguru import logger
from core.hap_manager import HapManager
from core.config import load_config

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
def cli(debug):
    if debug:
        logger.add("debug.log", level="DEBUG", rotation="10 MB")
        logger.debug("Debug mode enabled")

@cli.command()
@click.argument('input_hap', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
def unpack(input_hap, output_dir):
    try:
        logger.info(f"Unpacking {input_hap} to {output_dir}")
        manager = HapManager()
        manager.unpack(input_hap, output_dir)
    except Exception as e:
        logger.error(f"Failed to unpack: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_hap', type=click.Path())
@click.option('--sign/--no-sign', default=True, help='Sign the HAP file after packing')
def pack(input_dir, output_hap, sign):
    try:
        logger.info(f"Packing {input_dir} to {output_hap}")
        manager = HapManager()
        manager.pack(input_dir, output_hap, sign)
    except Exception as e:
        logger.error(f"Failed to pack: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.argument('hap_path', type=click.Path(exists=True))
@click.option('--bundle', '-b', default="com.echochat.hws", help='Bundle name')
@click.option('--ability', '-a', default="EntryAbility", help='Ability name')
def install(hap_path, bundle, ability):
    try:
        logger.info(f"Installing {hap_path}")
        manager = HapManager()
        manager.install(hap_path, bundle, ability)
    except Exception as e:
        logger.error(f"Failed to install: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    load_config()
    cli()