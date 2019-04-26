# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from functools import lru_cache, wraps
import logging

import pandas as pd
import numpy as np

from reco_utils.common.constants import (
    DEFAULT_USER_COL,
    DEFAULT_ITEM_COL,
    DEFAULT_RATING_COL,
    DEFAULT_LABEL_COL,
)


logger = logging.getLogger(__name__)


def user_item_pairs(
    user_df,
    item_df,
    user_col=DEFAULT_USER_COL,
    item_col=DEFAULT_ITEM_COL,
    user_item_filter_df=None,
    shuffle=True,
):
    """Get all pairs of users and items data.

    Args:
        user_df (pd.DataFrame): User data containing unique user ids and maybe their features.
        item_df (pd.DataFrame): Item data containing unique item ids and maybe their features.
        user_col (str): User id column name.
        item_col (str): Item id column name.
        user_item_filter_df (pd.DataFrame): User-item pairs to be used as a filter.
        shuffle (bool): If True, shuffles the result.

    Returns:
        pd.DataFrame: All pairs of user-item from user_df and item_df, excepting the pairs in user_item_filter_df
    """

    # Get all user-item pairs
    user_df["key"] = 1
    item_df["key"] = 1
    users_items = user_df.merge(item_df, on="key")

    user_df.drop("key", axis=1, inplace=True)
    item_df.drop("key", axis=1, inplace=True)
    users_items.drop("key", axis=1, inplace=True)

    # Filter
    if user_item_filter_df is not None:
        users_items = filter_by(users_items, user_item_filter_df, [user_col, item_col])

    if shuffle:
        users_items = users_items.sample(frac=1).reset_index(drop=True)

    return users_items


def filter_by(df, filter_by_df, filter_by_cols):
    """From the input DataFrame (df), remove the records whose target column (filter_by_cols) values are
    exist in the filter-by DataFrame (filter_by_df)

    Args:
        df (pd.DataFrame): Source dataframe.
        filter_by_df (pd.DataFrame): Filter dataframe.
        filter_by_cols (iterable of str): Filter columns.

    Returns:
        pd.DataFrame: Dataframe filtered by filter_by_df on filter_by_cols
    """

    return df.loc[
        ~df.set_index(filter_by_cols).index.isin(
            filter_by_df.set_index(filter_by_cols).index
        )
    ]


class LibffmConverter(object):
    """Converts an input Dataframe (df) to another Dataframe (df) in libffm format. A text file of the converted
    Dataframe is optionally generated.

    Note:
        The input dataframe is expected to represent the feature data in the following schema
        |field-1|field-2|...|field-n|rating|
        |feature-1-1|feature-2-1|...|feature-n-1|1|
        |feature-1-2|feature-2-2|...|feature-n-2|0|
        ...
        |feature-1-i|feature-2-j|...|feature-n-k|0|
        Where
        1. each "field-*" is the column name of the dataframe (column of lable/rating is excluded), and
        2. "feature-*-*" can be either a string or a numerical value, representing the categorical variable or
        actual numerical variable of the feature value in the field, respectively.
        3. If there are ordinal variables represented in int types, users should make sure these columns
        are properly converted to string type.

        The above data will be converted to the libffm format by following the convention as explained in
        https://www.csie.ntu.edu.tw/~r01922136/slides/ffm.pdf

        i.e., <field_index>:<field_feature_index>:1 or <field_index>:<field_index>:<field_feature_value>, depending on
        the data type of the features in the original dataframe.

    Examples:
        >>> import pandas as pd
        >>> df_feature = pd.DataFrame({
                'rating': [1, 0, 0, 1, 1],
                'field1': ['xxx1', 'xxx2', 'xxx4', 'xxx4', 'xxx4'],
                'field2': [3, 4, 5, 6, 7],
                'field3': [1.0, 2.0, 3.0, 4.0, 5.0],
                'field4': ['1', '2', '3', '4', '5']
            })
        >>> converter = LibffmConveter().fit(df_feature, col_rating='rating')
        >>> df_out = converter.transform(df_feature)
        >>> df_out
            rating field1 field2   field3 field4
        0       1  1:1:1  2:2:3  3:3:1.0  4:4:1
        1       0  1:2:1  2:2:4  3:3:2.0  4:5:1
        2       0  1:3:1  2:2:5  3:3:3.0  4:6:1
        3       1  1:3:1  2:2:6  3:3:4.0  4:7:1
        4       1  1:3:1  2:2:7  3:3:5.0  4:8:1

    Args:
        filepath (str): path to save the converted data.

    Attributes:
        field_count (int): count of field in the libffm format data
        feature_count (int): count of feature in the libffm format data
        filepath (str or None): file path where the output is stored - it can be None or a string
    """

    def __init__(self, filepath=None):
        self.filepath = filepath

    def fit(self, df, col_rating=DEFAULT_RATING_COL):
        """Fit the dataframe for libffm format. In there method does nothing but check the validity of 
        the input columns

        Args:
            df (pd.DataFrame): input Pandas dataframe.
            col_rating (str): rating of the data.

        Return:
            obj: the instance of the converter
        """
        # Check column types.
        types = df.dtypes
        if not all(
            [
                x == object or np.issubdtype(x, np.integer) or x == np.float
                for x in types
            ]
        ):
            raise TypeError("Input columns should be only object and/or numeric types.")

        if col_rating not in df.columns:
            raise TypeError(
                "Column of {} is not in input dataframe columns".format(col_rating)
            )

        self.col_rating = col_rating
        self.field_names = list(df.drop(col_rating, axis=1).columns)

        return self

    def transform(self, df):
        """Tranform an input dataset with the same schema (column names and dtypes) to libffm format 
        by using the fitted converter.

        Args: 
            df (pd.DataFrame): input Pandas dataframe.

        Return:
            pd.DataFrame: output libffm format dataframe.
        """
        if not self.col_rating in df.columns:
            raise ValueError(
                "Input dataset does not contain the label column {} in the fitting dataset".format(
                    self.col_rating
                )
            )

        if not all([x in df.columns for x in self.field_names]):
            raise ValueError(
                "Not all columns in the input dataset appear in the fitting dataset"
            )

        # Encode field-feature.
        idx = 1
        field_feature_dict = {}
        for field in self.field_names:
            if df[field].dtype == object:
                for feature in df[field].values:
                    # Check whether (field, feature) tuple exists in the dict or not.
                    # If not, put them into the key-values of the dict and count the index.
                    if (field, feature) not in field_feature_dict:
                        field_feature_dict[(field, feature)] = idx
                        idx += 1

        self.field_count = len(self.field_names)
        self.feature_count = idx - 1

        def _convert(field, feature, field_index, field_feature_index_dict):
            if isinstance(feature, str):
                field_feature_index = field_feature_index_dict[(field, feature)]
                feature = 1
            else:
                field_feature_index = field_index
            return "{}:{}:{}".format(field_index, field_feature_index, feature)

        for col_index, col in enumerate(self.field_names):
            df[col] = df[col].apply(
                lambda x: _convert(col, x, col_index + 1, field_feature_dict)
            )

        # Move rating column to the first.
        column_names = self.field_names[:]
        column_names.insert(0, self.col_rating)
        df = df[column_names]

        if self.filepath is not None:
            np.savetxt(self.filepath, df.values, delimiter=" ", fmt="%s")

        return df

    def fit_transform(self, df, col_rating=DEFAULT_RATING_COL):
        """Do fit and transform in a row

        Args:
            df (pd.DataFrame): input Pandas dataframe.
            col_rating (str): rating of the data.

        Return:
            pd.DataFrame: output libffm format dataframe.
        """
        return self.fit(df, col_rating=col_rating).transform(df)

    def get_params(self):
        """Get parameters (attributes) of the libffm converter

        Return:
            dict: parameters field count, feature count, and file path.
        """
        return {
            "field count": self.field_count,
            "feature count": self.feature_count,
            "file path": self.filepath,
        }


def negative_feedback_sampler(
    df,
    col_user=DEFAULT_USER_COL,
    col_item=DEFAULT_ITEM_COL,
    col_label=DEFAULT_LABEL_COL,
    ratio_neg_per_user=1,
    seed=42,
):
    """Utility function to sample negative feedback from user-item interaction dataset.

    This negative sampling function will take the user-item interaction data to create 
    binarized feedback, i.e., 1 and 0 indicate positive and negative feedback, 
    respectively. 

    Negative sampling is used in the literature frequently to generate negative samples 
    from a user-item interaction data.
    See for example the neural collaborative filtering paper 
    https://www.comp.nus.edu.sg/~xiangnan/papers/ncf.pdf
    
    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
            'userID': [1, 2, 3],
            'itemID': [1, 2, 3],
            'rating': [5, 5, 5]
        })
        >>> df_neg_sampled = negative_feedback_sampler(
            df, col_user='userID', col_item='itemID', ratio_neg_per_user=1
        )
        >>> df_neg_sampled
        userID  itemID  feedback
        1   1   1
        1   2   0
        2   2   1
        2   1   0
        3   3   1
        3   1   0

    Args:
        df (pandas.DataFrame): input data that contains user-item tuples.
        col_user (str): user id column name.
        col_item (str): item id column name.
        col_label (str): label column name. It is used for the generated columns where labels
        of positive and negative feedback, i.e., 1 and 0, respectively, in the output dataframe.
        ratio_neg_per_user (int): ratio of negative feedback w.r.t to the number of positive feedback for each user. 
        If the samples exceed the number of total possible negative feedback samples, it will be reduced to the number
        of all the possible samples.
        seed (int): seed for the random state of the sampling function.

    Returns:
        pandas.DataFrame: data with negative feedback 
    """
    # Get all of the users and items.
    users = df[col_user].unique()
    items = df[col_item].unique()

    # Create a dataframe for all user-item pairs
    df_neg = user_item_pairs(
        pd.DataFrame(users, columns=[col_user]),
        pd.DataFrame(items, columns=[col_item]),
        user_item_filter_df=df,
    )
    df_neg[col_label] = 0

    df_pos = df.copy()
    df_pos[col_label] = 1

    df_all = pd.concat([df_pos, df_neg], ignore_index=True, sort=True)
    df_all = df_all[[col_user, col_item, col_label]]

    # Sample negative feedback from the combined dataframe.
    df_sample = (
        df_all.groupby(col_user)
        .apply(
            lambda x: pd.concat(
                [
                    x[x[col_label] == 1],
                    x[x[col_label] == 0].sample(
                        min(
                            max(
                                round(len(x[x[col_label] == 1]) * ratio_neg_per_user), 1
                            ),
                            len(x[x[col_label] == 0]),
                        ),
                        random_state=seed,
                        replace=False,
                    )
                    if len(x[x[col_label] == 0] > 0)
                    else pd.DataFrame({}, columns=[col_user, col_item, col_label]),
                ],
                ignore_index=True,
                sort=True,
            )
        )
        .reset_index(drop=True)
        .sort_values(col_user)
    )

    return df_sample


def has_columns(df, columns):
    """Check if DataFrame has necessary columns

    Args:
        df (pd.DataFrame): DataFrame
        columns (list(str): columns to check for

    Returns:
        bool: True if DataFrame has specified columns
    """

    result = True
    for column in columns:
        if column not in df.columns:
            logger.error("Missing column: {} in DataFrame".format(column))
            result = False

    return result


def has_same_base_dtype(df_1, df_2, columns=None):
    """Check if specified columns have the same base dtypes across both DataFrames

    Args:
        df_1 (pd.DataFrame): first DataFrame
        df_2 (pd.DataFrame): second DataFrame
        columns (list(str)): columns to check, None checks all columns

    Returns:
        bool: True if DataFrames columns have the same base dtypes
    """

    if columns is None:
        if any(set(df_1.columns).symmetric_difference(set(df_2.columns))):
            logger.error(
                "Cannot test all columns because they are not all shared across DataFrames"
            )
            return False
        columns = df_1.columns

    if not (
        has_columns(df=df_1, columns=columns) and has_columns(df=df_2, columns=columns)
    ):
        return False

    result = True
    for column in columns:
        if df_1[column].dtype.type.__base__ != df_2[column].dtype.type.__base__:
            logger.error("Columns {} do not have the same base datatype".format(column))
            result = False

    return result


class PandasHash:
    """Wrapper class to allow pandas objects (DataFrames or Series) to be hashable"""

    # reserve space just for a single pandas object
    __slots__ = 'pandas_object'

    def __init__(self, pandas_object):
        """Initialize class
        Args:
            pandas_object (pd.DataFrame|pd.Series): pandas object
        """

        if not isinstance(pandas_object, (pd.DataFrame, pd.Series)):
            raise TypeError('Can only wrap pandas DataFrame or Series objects')
        self.pandas_object = pandas_object

    def __eq__(self, other):
        """Overwrite equality comparison
        Args:
            other (pd.DataFrame|pd.Series): pandas object to compare

        Returns:
            bool: whether other object is the same as this one
        """

        return hash(self) == hash(other)

    def __hash__(self):
        """Overwrite hash operator for use with pandas objects

        Returns:
            int: hashed value of object
        """

        hashable = tuple(self.pandas_object.values.tobytes())
        if isinstance(self.pandas_object, pd.DataFrame):
            hashable += tuple(self.pandas_object.columns)
        else:
            hashable += tuple(self.pandas_object.name)
        return hash(hashable)


def lru_cache_df(maxsize, typed=False):
    """Least-recently-used cache decorator

    Args:
        maxsize (int|None): max size of cache, if set to None cache is boundless
        typed (bool): arguments of different types are cached separately
    """

    def to_pandas_hash(val):
        """Return PandaHash object if input is a DataFrame otherwise return input unchanged"""
        return PandasHash(val) if isinstance(val, pd.DataFrame) else val

    def from_pandas_hash(val):
        """Extract DataFrame if input is PandaHash object otherwise return input unchanged"""
        return val.pandas_object if isinstance(val, PandasHash) else val

    def decorating_function(user_function):
        @wraps(user_function)
        def wrapper(*args, **kwargs):
            # convert DataFrames in args and kwargs to PandaHash objects
            args = tuple([to_pandas_hash(a) for a in args])
            kwargs = {k: to_pandas_hash(v) for k, v in kwargs.items()}
            return cached_wrapper(*args, **kwargs)

        @lru_cache(maxsize=maxsize, typed=typed)
        def cached_wrapper(*args, **kwargs):
            # get DataFrames from PandaHash objects in args and kwargs
            args = tuple([from_pandas_hash(a) for a in args])
            kwargs = {k: from_pandas_hash(v) for k, v in kwargs.items()}
            return user_function(*args, **kwargs)

        # retain lru_cache attributes
        wrapper.cache_info = cached_wrapper.cache_info
        wrapper.cache_clear = cached_wrapper.cache_clear

        return wrapper
    return decorating_function
