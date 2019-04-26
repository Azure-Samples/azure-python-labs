# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import re
import shutil
import warnings
import pandas as pd
from zipfile import ZipFile
from reco_utils.dataset.download_utils import maybe_download, download_path
from reco_utils.common.notebook_utils import is_databricks
from reco_utils.common.constants import (
    DEFAULT_USER_COL,
    DEFAULT_ITEM_COL,
    DEFAULT_RATING_COL,
    DEFAULT_TIMESTAMP_COL,
)

try:
    from pyspark.sql.types import (
        StructType,
        StructField,
        IntegerType,
        FloatType,
        DoubleType,
        LongType,
        StringType,
    )
    from pyspark.sql.functions import concat_ws, col
except ImportError:
    pass  # so the environment without spark doesn't break


class _DataFormat:
    def __init__(
        self,
        sep,
        path,
        has_header=False,
        item_sep=None,
        item_path=None,
        item_has_header=False,
    ):
        """MovieLens data format container as a different size of MovieLens data file
        has a different format

        Args:
            sep (str): Rating data delimiter
            path (str): Rating data path within the original zip file
            has_header (bool): Whether the rating data contains a header line or not
            item_sep (str): Item data delimiter
            item_path (str): Item data path within the original zip file
            item_has_header (bool): Whether the item data contains a header line or not
        """

        # Rating file
        self._sep = sep
        self._path = path
        self._has_header = has_header

        # Item file
        self._item_sep = item_sep
        self._item_path = item_path
        self._item_has_header = item_has_header

    """ Rating file """

    @property
    def separator(self):
        return self._sep

    @property
    def path(self):
        return self._path

    @property
    def has_header(self):
        return self._has_header

    """ Item (Movie) file """

    @property
    def item_separator(self):
        return self._item_sep

    @property
    def item_path(self):
        return self._item_path

    @property
    def item_has_header(self):
        return self._item_has_header


# 10m and 20m data do not have user data
DATA_FORMAT = {
    "100k": _DataFormat("\t", "ml-100k/u.data", False, "|", "ml-100k/u.item", False),
    "1m": _DataFormat(
        "::", "ml-1m/ratings.dat", False, "::", "ml-1m/movies.dat", False
    ),
    "10m": _DataFormat(
        "::", "ml-10M100K/ratings.dat", False, "::", "ml-10M100K/movies.dat", False
    ),
    "20m": _DataFormat(",", "ml-20m/ratings.csv", True, ",", "ml-20m/movies.csv", True),
}

# 100K data genres index to string mapper. For 1m, 10m, and 20m, the genres labels are already in the dataset.
GENRES = (
    "unknown",
    "Action",
    "Adventure",
    "Animation",
    "Children's",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
)

DEFAULT_HEADER = (
    DEFAULT_USER_COL,
    DEFAULT_ITEM_COL,
    DEFAULT_RATING_COL,
    DEFAULT_TIMESTAMP_COL,
)

# Warning and error messages
WARNING_MOVIE_LENS_HEADER = """MovieLens rating dataset has four columns
    (user id, movie id, rating, and timestamp), but more than four column names are provided.
    Will only use the first four column names."""
WARNING_HAVE_SCHEMA_AND_HEADER = """Both schema and header are provided.
    The header argument will be ignored."""
ERROR_MOVIE_LENS_SIZE = "Invalid data size. Should be one of {100k, 1m, 10m, or 20m}"
ERROR_NO_HEADER = "No header (schema) information. At least user and movie column names should be provided"


def load_pandas_df(
    size="100k",
    header=DEFAULT_HEADER,
    local_cache_path=None,
    title_col=None,
    genres_col=None,
    year_col=None,
):
    """Loads the MovieLens dataset as pd.DataFrame.

    Download the dataset from http://files.grouplens.org/datasets/movielens, unzip, and load.
    To load movie information only, you can use load_item_df function. 

    Args:
        size (str): Size of the data to load. One of ("100k", "1m", "10m", "20m").
        header (list or tuple or None): Rating dataset header.
        local_cache_path (str): Path (directory or a zip file) to cache the downloaded zip file.
            If None, all the intermediate files will be stored in a temporary directory and removed after use.
        title_col (str): Movie title column name. If None, the column will not be loaded.
        genres_col (str): Genres column name. Genres are '|' separated string.
            If None, the column will not be loaded.
        year_col (str): Movie release year column name. If None, the column will not be loaded.

    Returns:
        pd.DataFrame: Movie rating dataset.
        
    Examples:
        To load just user-id, item-id, and ratings from MovieLens-1M dataset,
        >>> df = load_pandas_df('1m', ('UserId', 'ItemId', 'Rating'))

        To load rating's timestamp together,
        >>> df = load_pandas_df('1m', ('UserId', 'ItemId', 'Rating', 'Timestamp'))

        To load movie's title, genres, and released year info along with the ratings data,
        >>> df = load_pandas_df('1m', ('UserId', 'ItemId', 'Rating', 'Timestamp'),
        ...     title_col='Title',
        ...     genres_col='Genres',
        ...     year_col='Year'
        ... )
    """
    size = size.lower()
    if size not in DATA_FORMAT:
        raise ValueError(ERROR_MOVIE_LENS_SIZE)

    if header is None or len(header) < 2:
        raise ValueError(ERROR_NO_HEADER)
    elif len(header) > 4:
        warnings.warn(WARNING_MOVIE_LENS_HEADER)
        header = header[:4]

    movie_col = header[1]

    with download_path(local_cache_path) as path:
        filepath = os.path.join(path, "ml-{}.zip".format(size)) 
        datapath, item_datapath = _maybe_download_and_extract(size, filepath)

        # Load movie features such as title, genres, and release year
        item_df = _load_item_df(
            size, item_datapath, movie_col, title_col, genres_col, year_col
        )

        # Load rating data
        df = pd.read_csv(
            datapath,
            sep=DATA_FORMAT[size].separator,
            engine="python",
            names=header,
            usecols=[*range(len(header))],
            header=0 if DATA_FORMAT[size].has_header else None,
        )

        # Convert 'rating' type to float
        if len(header) > 2:
            df[header[2]] = df[header[2]].astype(float)

        # Merge rating df w/ item_df
        if item_df is not None:
            df = df.merge(item_df, on=header[1])

    return df


def load_item_df(
    size="100k",
    local_cache_path=None,
    movie_col=DEFAULT_ITEM_COL,
    title_col=None,
    genres_col=None,
    year_col=None,
):
    """Loads Movie info.

    Args:
        size (str): Size of the data to load. One of ("100k", "1m", "10m", "20m").
        local_cache_path (str): Path (directory or a zip file) to cache the downloaded zip file.
            If None, all the intermediate files will be stored in a temporary directory and removed after use.
        movie_col (str): Movie id column name.
        title_col (str): Movie title column name. If None, the column will not be loaded.
        genres_col (str): Genres column name. Genres are '|' separated string.
            If None, the column will not be loaded.
        year_col (str): Movie release year column name. If None, the column will not be loaded.

    Returns:
        pd.DataFrame: Movie information data, such as title, genres, and release year.
    """
    size = size.lower()
    if size not in DATA_FORMAT:
        raise ValueError(ERROR_MOVIE_LENS_SIZE)

    with download_path(local_cache_path) as path:
        filepath = os.path.join(path, "ml-{}.zip".format(size)) 
        _, item_datapath = _maybe_download_and_extract(size, filepath)
        item_df = _load_item_df(
            size, item_datapath, movie_col, title_col, genres_col, year_col
        )

    return item_df


def _load_item_df(size, item_datapath, movie_col, title_col, genres_col, year_col):
    """Loads Movie info"""
    if title_col is None and genres_col is None and year_col is None:
        return None

    item_header = [movie_col]
    usecols = [0]

    # Year is parsed from title
    if title_col is not None or year_col is not None:
        item_header.append("title_year")
        usecols.append(1)

    genres_header_100k = None
    if genres_col is not None:
        # 100k data's movie genres are encoded as a binary array (the last 19 fields)
        # For details, see http://files.grouplens.org/datasets/movielens/ml-100k-README.txt
        if size == "100k":
            genres_header_100k = [*(str(i) for i in range(19))]
            item_header.extend(genres_header_100k)
            usecols.extend([*range(5, 24)])  # genres columns
        else:
            item_header.append(genres_col)
            usecols.append(2)  # genres column

    item_df = pd.read_csv(
        item_datapath,
        sep=DATA_FORMAT[size].item_separator,
        engine="python",
        names=item_header,
        usecols=usecols,
        header=0 if DATA_FORMAT[size].item_has_header else None,
        encoding="ISO-8859-1",
    )

    # Convert 100k data's format: '0|0|1|...' to 'Action|Romance|..."
    if genres_header_100k is not None:
        item_df[genres_col] = item_df[genres_header_100k].values.tolist()
        item_df[genres_col] = item_df[genres_col].map(
            lambda l: "|".join([GENRES[i] for i, v in enumerate(l) if v == 1])
        )

        item_df.drop(genres_header_100k, axis=1, inplace=True)

    # Parse year from movie title. Note, MovieLens title format is "title (year)"
    # Note, there are very few records that are missing the year info.
    if year_col is not None:

        def parse_year(t):
            parsed = re.split("[()]", t)
            if len(parsed) > 2 and parsed[-2].isdecimal():
                return parsed[-2]
            else:
                return None

        item_df[year_col] = item_df["title_year"].map(parse_year)
        if title_col is None:
            item_df.drop("title_year", axis=1, inplace=True)

    if title_col is not None:
        item_df.rename(columns={"title_year": title_col}, inplace=True)

    return item_df


def load_spark_df(
    spark,
    size="100k",
    header=DEFAULT_HEADER,
    schema=None,
    local_cache_path=None,
    dbutils=None,
    title_col=None,
    genres_col=None,
    year_col=None,
):
    """Loads the MovieLens dataset as pySpark.DataFrame.

    Download the dataset from http://files.grouplens.org/datasets/movielens, unzip, and load
    To load movie information only, you can use load_item_df function. 

    Args:
        spark (pySpark.SparkSession)
        size (str): Size of the data to load. One of ("100k", "1m", "10m", "20m").
        header (list or tuple): Rating dataset header.
            If schema is provided, this argument is ignored.
        schema (pySpark.StructType): Dataset schema. By default,
            StructType(
                [
                    StructField(DEFAULT_USER_COL, IntegerType()),
                    StructField(DEFAULT_ITEM_COL, IntegerType()),
                    StructField(DEFAULT_RATING_COL, FloatType()),
                    StructField(DEFAULT_TIMESTAMP_COL, LongType()),
                ]
            )
        local_cache_path (str): Path (directory or a zip file) to cache the downloaded zip file.
            If None, all the intermediate files will be stored in a temporary directory and removed after use.
        dbutils (Databricks.dbutils): Databricks utility object
        title_col (str): Title column name. If None, the column will not be loaded.
        genres_col (str): Genres column name. Genres are '|' separated string.
            If None, the column will not be loaded.
        year_col (str): Movie release year column name. If None, the column will not be loaded.

    Returns:
        pySpark.DataFrame: Movie rating dataset.
        
    Examples:
        To load just user-id, item-id, and ratings from MovieLens-1M dataset,
        >>> spark_df = load_spark_df(spark, '1m', ('UserId', 'ItemId', 'Rating'))

        To load rating's timestamp together,
        >>> spark_df = load_spark_df(spark, '1m', ('UserId', 'ItemId', 'Rating', 'Timestamp'))

        To load movie's title, genres, and released year info along with the ratings data,
        >>> spark_df = load_spark_df(spark, '1m', ('UserId', 'ItemId', 'Rating', 'Timestamp'),
        ...     title_col='Title',
        ...     genres_col='Genres',
        ...     year_col='Year'
        ... )

        On DataBricks, pass the dbutils argument as follows:
        >>> spark_df = load_spark_df(spark, dbutils=dbutils)
    """
    size = size.lower()
    if size not in DATA_FORMAT:
        raise ValueError(ERROR_MOVIE_LENS_SIZE)

    schema = _get_schema(header, schema)
    if schema is None or len(schema) < 2:
        raise ValueError(ERROR_NO_HEADER)

    movie_col = schema[1].name

    with download_path(local_cache_path) as path:
        filepath = os.path.join(path, "ml-{}.zip".format(size)) 
        datapath, item_datapath = _maybe_download_and_extract(size, filepath)
        spark_datapath = "file:///" + datapath  # shorten form of file://localhost/

        # Load movie features such as title, genres, and release year.
        # Since the file size is small, we directly load as pd.DataFrame from the driver node
        # and then convert into spark.DataFrame
        item_pd_df = _load_item_df(size, item_datapath, movie_col, title_col, genres_col, year_col)
        item_df = spark.createDataFrame(item_pd_df) if item_pd_df is not None else None

        if is_databricks():
            if dbutils is None:
                raise ValueError(
                    """
                    To use on a Databricks, dbutils object should be passed as an argument.
                    E.g. load_spark_df(spark, dbutils=dbutils)
                """
                )

            # Move rating file to DBFS in order to load into spark.DataFrame
            dbfs_datapath = "dbfs:/tmp/" + datapath
            dbutils.fs.mv(spark_datapath, dbfs_datapath)
            spark_datapath = dbfs_datapath

        # pySpark's read csv currently doesn't support multi-character delimiter, thus we manually handle that
        separator = DATA_FORMAT[size].separator
        if len(separator) > 1:
            raw_data = spark.sparkContext.textFile(spark_datapath)
            data_rdd = raw_data.map(lambda l: l.split(separator)).map(
                lambda c: [int(c[0]), int(c[1]), float(c[2]), int(c[3])][: len(schema)]
            )
            df = spark.createDataFrame(data_rdd, schema)
        else:
            df = spark.read.csv(
                spark_datapath,
                schema=schema,
                sep=separator,
                header=DATA_FORMAT[size].has_header,
            )

        # Merge rating df w/ item_df
        if item_df is not None:
            df = df.join(item_df, movie_col, "left")

        # Cache and force trigger action since data-file might be removed.
        df.cache()
        df.count()

    return df


def _get_schema(header, schema):
    if schema is None or len(schema) == 0:
        # Use header to generate schema
        if header is None or len(header) == 0:
            return None
        elif len(header) > 4:
            warnings.warn(WARNING_MOVIE_LENS_HEADER)
            header = header[:4]

        schema = StructType()
        try:
            schema.add(StructField(header[0], IntegerType())).add(
                StructField(header[1], IntegerType())
            ).add(StructField(header[2], FloatType())).add(
                StructField(header[3], LongType())
            )
        except IndexError:
            pass
    else:
        if header is not None:
            warnings.warn(WARNING_HAVE_SCHEMA_AND_HEADER)

        if len(schema) > 4:
            warnings.warn(WARNING_MOVIE_LENS_HEADER)
            schema = schema[:4]

    return schema


def _maybe_download_and_extract(size, dest_path):
    """Downloads and extracts MovieLens rating and item datafiles if they don’t already exist"""
    dirs, _ = os.path.split(dest_path)
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    _, rating_filename = os.path.split(DATA_FORMAT[size].path)
    rating_path = os.path.join(dirs, rating_filename)
    _, item_filename = os.path.split(DATA_FORMAT[size].item_path)
    item_path = os.path.join(dirs, item_filename)

    if not os.path.exists(rating_path) or not os.path.exists(item_path):
        download_movielens(size, dest_path)
        extract_movielens(size, rating_path, item_path, dest_path)

    return rating_path, item_path


def download_movielens(size, dest_path):
    """Downloads MovieLens datafile.

    Args:
        size (str): Size of the data to load. One of ("100k", "1m", "10m", "20m").
        dest_path (str): File path for the downloaded file
    """
    if size not in DATA_FORMAT:
        raise ValueError(ERROR_MOVIE_LENS_SIZE)

    url = "http://files.grouplens.org/datasets/movielens/ml-" + size + ".zip"
    dirs, file = os.path.split(dest_path)
    maybe_download(url, file, work_directory=dirs)


def extract_movielens(size, rating_path, item_path, zip_path):
    """Extract MovieLens rating and item datafiles from the MovieLens raw zip file.

    To extract all files instead of just rating and item datafiles,
    use ZipFile's extractall(path) instead.

    Args:
        size (str): Size of the data to load. One of ("100k", "1m", "10m", "20m").
        rating_path (str): Destination path for rating datafile
        item_path (str): Destination path for item datafile
        zip_path (str): zipfile path
    """
    with ZipFile(zip_path, "r") as z:
        with z.open(DATA_FORMAT[size].path) as zf, open(rating_path, "wb") as f:
            shutil.copyfileobj(zf, f)
        with z.open(DATA_FORMAT[size].item_path) as zf, open(item_path, "wb") as f:
            shutil.copyfileobj(zf, f)
