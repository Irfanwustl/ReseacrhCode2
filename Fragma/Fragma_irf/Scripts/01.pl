#!/usr/bin/perl
use v5.16;
use strict;
use warnings;

my $file="$ARGV[0]";

open IN,"$file";
while(<IN>){
	chomp;
	my @tmp = split /\t/;
	if($tmp[3]==1){
		print "$tmp[0]\t$tmp[1]\t$tmp[2]\t$tmp[4]";
	}else{
		print "\t$tmp[4]";
	}
	if($tmp[3]==12){
		print "\n";
	}
}
close IN;

